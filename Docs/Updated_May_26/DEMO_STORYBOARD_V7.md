# Machina OS — Demo Storyboard v7

> A scripted walkthrough to test Machina OS end-to-end.
> Updated for Sprint 60+ (chain persistence, debug execution, studio enhancements).
> Each act exercises a specific capability. Acts are ordered from simple to complex.
> See also: [MULTI_AGENT_MANUAL.md](MULTI_AGENT_MANUAL.md) for a dedicated deep-dive into all multi-agent features.
> See also: [machinaos_mcp_manual.md](machinaos_mcp_manual.md) for a dedicated MCP protocol walkthrough.

---

## Prerequisites

```bash
# 1. Start the server
cd machina-os
python -m uvicorn apps.api.server:app --host 127.0.0.1 --port 8100

# 2. Open the UI
# Navigate to http://127.0.0.1:8100

# 3. (Optional) LLM backend for conversational features
#    Supports 7 providers: Ollama, OpenAI, Gemini, Claude, OpenRouter, LM Studio, GitHub Copilot
#    Set MACHINA_LLM_PROVIDER, MACHINA_LLM_URL, MACHINA_LLM_MODEL, MACHINA_LLM_API_KEY

# 4. (Optional) Desktop shell: cd desktop && npm run dev
#    Or install from MSI/NSIS package (zero-prerequisite, bundles Python)

# 5. Port conflict auto-recovery: if 8100 is busy, the server detects it,
#    identifies the holder via netstat, and offers to kill the stale process.

# 6. (Optional) MCP servers: requires Node.js / npx for default MCP servers
#    3 servers auto-connect on startup (sequential-thinking, memory, fetch)
#    GitHub MCP server requires GITHUB_PERSONAL_ACCESS_TOKEN env var
```

---

## System Overview

| Metric | Value |
|--------|-------|
| Version | 0.2.0 |
| API Endpoints | 227 |
| Registered Tools | 52 base (across 9 domains) + MCP-bridged tools + 4 MCP virtual tools |
| UI Views | 16 (+ Security Center + MCP) |
| Test Suite | 2273 tests |
| Build Items | 581 |
| Sprints Completed | 62 |
| Builtin Agents | 6 (filesystem, git, shell, system, mcp, + user-created) |
| Agent Blueprint Templates | 21 |
| Orchestration Strategies | 5 (SINGLE, ROUND_ROBIN, CAPABILITY_SCORE, FALLBACK, PIPELINE) |
| Chain Templates | 35 |
| Workflow DSL Templates | 24 |
| LLM Providers | 6 in dropdown (Ollama, OpenAI, Gemini, Claude, OpenRouter, LM Studio) + GitHub via dedicated panel |
| Security Modules | 4 (Encryption, Scrubber, Audit Log, Vulnerability Analyzer) |
| MCP Protocol | Dual-role: JSON-RPC 2.0 **client** (stdio + SSE) + **server/provider** (SSE transport); tool/resource/prompt bridges; 5 default servers (3 auto-connect); MCPServer exposes all tools + 17 resources + 4 prompts + 4 virtual tools to external clients (Claude Desktop, Cursor, etc.) |
| Agent Sub-Tabs | 6 (Fleet, Coordination, Performance, Monitoring, Pipelines, Communications) |
| Desktop Shell | Tauri 2 (Windows/Linux/macOS) with auto-updater |
| Demo Mode | 3 tiers (INTERNAL, REVIEWER, DEMO) |
| GitHub Integration | Dedicated connection panel (PAT), status bar dot, API validation; 7 tools (`github.list_repos`, `github.repo_info`, `github.list_branches`, `github.list_issues`, `github.list_prs`, `github.create_issue`, `github.clone`); in-UI GitHub Explorer with repo cards + action buttons; intent-routed chat commands |
| Default MCP Servers | 5 pre-configured: sequential-thinking ✅, memory ✅, fetch ✅, github ❌ (needs PAT), sqlite ❌ (needs db path) |

---

## Act 1 — System Boot & Health

**Goal:** Verify the system starts cleanly and the Home dashboard renders with live data.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 1.1 | Open `http://127.0.0.1:8100` | Browser | Home dashboard loads with glassmorphic cards. Orb animation plays. |
| 1.2 | Check **4 health cards** on Home | Dashboard | Memory Usage (bar), LLM Provider (status dot), Agent Fleet (online/degraded/offline counts), Registered Tools (count). All show live data. |
| 1.3 | Check **Events Today** sidebar | Dashboard right | Shows recent events with type badges and relative timestamps. |
| 1.4 | Check **Workspace Context** panel | Dashboard | Shows indexed workspace info: languages, frameworks, key files, git status. |
| 1.5 | Check **System Status Bar** | Bottom bar | Shows workspace hostname, active tasks, agent fleet (online/total), memory usage, LLM status dot with provider name, GitHub connection dot (green=connected, grey=not connected). Refreshes every 30s. |
| 1.6 | Click **Tools** nav tab (or Ctrl+3) | Nav bar | Tools grid: 52 tools across filesystem, shell, process, browser, git, github, vscode, system. Risk badges (LOW/MEDIUM/HIGH). Click any tool to use it in chat. |
| 1.7 | `curl http://127.0.0.1:8100/health` | Terminal | `{"status":"ok","version":"0.2.0"}` |
| 1.8 | `curl http://127.0.0.1:8100/runtime/status` | Terminal | JSON with `tool_count: 52`, `total_tasks: 0`, `components` map. |
| 1.9 | `curl http://127.0.0.1:8100/system/status` | Terminal | Combined: tools count, system info (OS, CPU, RAM), memory/disk usage, agent fleet, active tasks. |

**Pass criteria:** Dashboard renders with live data, status bar refreshes (including LLM dot + GitHub status dot), health endpoints respond, tool count = 52, version = 0.2.0.

---

## Act 2 — Basic File Operations (Deterministic Planner)

**Goal:** Execute filesystem commands using the heuristic parser and deterministic planner. No LLM required.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 2.1 | Type `list .` in Neural Link | Chat | Plan card: `filesystem.list` → **completed**. Pretty output with 📁/📄 icons and sizes. |
| 2.2 | Type `read pyproject.toml` | Chat | Plan card: `filesystem.read_file` → shows file contents. |
| 2.3 | Type `create test_demo.txt "Hello from Machina OS"` | Chat | Plan card: `filesystem.write_file` → **completed**. Backup created as `.machina_bak`. |
| 2.4 | Type `delete test_demo.txt` | Chat | Plan card: `filesystem.delete` → requires **approval** (HIGH risk). |
| 2.5 | Type `tree .` | Chat | Plan card: `filesystem.tree` → directory structure with 📁/📄 indentation. |
| 2.6 | Type `search pyproject.toml .` | Chat | Plan card: `filesystem.search` → finds file with path and size. |
| 2.7 | Type `grep "FastAPI" .` | Chat | Plan card: `filesystem.grep` → matching lines with file paths and line numbers. |
| 2.8 | Type `system info` | Chat | Plan card: `system.info` → formatted key-value display (OS, hostname, CPU, RAM). |
| 2.9 | Click **Timeline** (Ctrl+8) | Nav | Task history with expand/collapse. Statuses match what happened. |
| 2.10 | Type `copy pyproject.toml pyproject_backup.toml` | Chat | Plan card: `filesystem.copy` → **completed**. Destination file created. |
| 2.11 | Type `mkdir sandbox/test_dir` | Chat | Plan card: `filesystem.mkdir` → **completed**. Directory tree created. |

**Pass criteria:** All filesystem operations succeed with pretty output. Copy and mkdir work. Timeline records each task.

---

## Act 3 — Shell Execution & Policy Gating

**Goal:** Test the shell runner (2 tools) with policy enforcement.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 3.1 | Type `run echo hello` | Chat | Plan: `shell.run` → **approval gate** (HIGH risk). Approve → output "hello". |
| 3.2 | Type `run dir` | Chat | Deterministic planner → `shell.run_safe` (MEDIUM risk, read-only). Output = directory listing. |
| 3.3 | Type `run rm -rf /` | Chat | `shell.run` → destructive command detection → **blocked** or approval-gated. |
| 3.4 | Type `run sudo apt install something` | Chat | Privilege escalation detection → **blocked**. |
| 3.5 | Type `run whoami` | Chat | Should use `shell.run_safe` (read-only). |
| 3.6 | Check Timeline | Timeline | Each shell step logged with correct risk level. |

**Pass criteria:** shell.run gated at HIGH. shell.run_safe permitted at MEDIUM. Destructive commands blocked.

---

## Act 4 — Conversational Multi-Turn (LLM Required)

**Goal:** Test multi-turn conversation with context retention.

> **Requires an active LLM provider.** Skip if no LLM configured.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 4.1 | Type `What is this project about?` | Chat | Conversational response with workspace context (detected languages, frameworks). |
| 4.2 | Type `What languages does it use?` | Chat | References prior context. Mentions detected languages. |
| 4.3 | Type `Summarize the README` | Chat | Triggers `filesystem.read_file` on README.md → LLM summary. |
| 4.4 | Type `What did I just ask?` | Chat | References conversation history accurately. |
| 4.5 | Press **Alt+N** | Chat | New conversation session. Previous context cleared. |

**Pass criteria:** Multi-turn context retained. Workspace context injected. Alt+N starts fresh session.

---

## Act 5 — Command Palette & Keyboard UX

**Goal:** Test the Ctrl+K fuzzy search and keyboard shortcuts.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 5.1 | Press **Ctrl+K** | Overlay | Command Palette opens with search field. |
| 5.2 | Type `tools` | Palette | "Go to Tools" highlighted. |
| 5.3 | Press **Enter** | Palette | Switches to Tools view. Palette closes. |
| 5.4 | Press **Ctrl+K**, type `agents` | Palette | Shows "Go to Agents". Enter → switches. |
| 5.5 | Press **Ctrl+K**, type `restart the server` | Palette | No match → "Send to Neural Link" → sends to chat. |
| 5.6 | Press **Ctrl+1** through **Ctrl+9** | Keyboard | Switches views in order: Home, Chat, Tools, Memory, Workflows, Studio, Agents, Timeline, Explorer. |
| 5.7 | Press **Ctrl+L** | Keyboard | Focuses the Neural Link input. |
| 5.8 | Press **Escape** | Keyboard | Clears input field. |

**Pass criteria:** Ctrl+K opens palette, fuzzy search works, unmatched sends to chat, view shortcuts work.

---

## Act 6 — File Explorer & Process Monitor

**Goal:** Test the file browser and process list views.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 6.1 | Click **Explorer** (Ctrl+9) | Nav | Split panel: directory tree (left) + file preview (right). |
| 6.2 | Click a folder | Explorer | Breadcrumb navigation updates. Directory listing loads. |
| 6.3 | Click **Go Up** (⬆) | Explorer | Navigates to parent directory. |
| 6.4 | Click a file | Explorer | Preview panel shows file contents (100KB cap). File-type icons. |
| 6.5 | Click **Processes** | Nav | Sortable table: PID, Name, Status, CPU%, Memory. |
| 6.6 | Type in search filter | Processes | Filters process list by name. |
| 6.7 | Click **Stop** on a process | Processes | Confirmation prompt → stops process. |

**Pass criteria:** Explorer navigates and previews. Process monitor shows live data with search + stop.

---

## Act 7 — Memory & Workspace Intelligence

**Goal:** Test memory scopes, preferences, personality, and workspace indexing.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 7.1 | Click **Memory** (Ctrl+4) | Nav | 4 tabs: Scopes, Preferences, Workspaces, Sessions. |
| 7.2 | Set a memory key in "session" scope | Memory | `PUT /memory/session/demo_key` → stored. |
| 7.3 | Retrieve it | Memory | Key-value displayed. |
| 7.4 | Check **Workspaces** tab | Memory | Indexed workspaces with languages, frameworks, key files, last_indexed timestamp. |
| 7.5 | Check **Personality** tab (Settings → Personality) | Settings | Presets: default, casual, minimal, detailed. Tone/verbosity/emoji/greeting controls. |
| 7.6 | Switch personality to "casual" | Settings | Conversational responses shift tone. |

**Pass criteria:** Memory CRUD works across scopes. Workspace auto-indexed. Personality affects responses.

---

## Act 8 — Error Handling & Recovery

**Goal:** Test failure recovery, retry, and explanation.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 8.1 | Type `read nonexistent_file.txt` | Chat | Plan step → **FAILED** with `FILE_NOT_FOUND` error. |
| 8.2 | Click **Retry** on failed step | Chat card | Step re-executes. |
| 8.3 | Click **Explain** on failed step | Chat card | LLM-powered (if LLM active) or fallback error analysis. |
| 8.4 | Check Timeline for error events | Timeline | `step_failed` event with error_code, severity=ERROR. |

**Pass criteria:** Errors classified correctly. Retry and explain buttons visible and functional.

---

## Act 9 — Git Integration (13 Tools)

**Goal:** Test all git tools and natural language git routing.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 9.1 | Type `git status` | Chat | Plan: `git.status` → branch name, clean/dirty indicator, file sections. |
| 9.2 | Type `git log` | Chat | Plan: `git.log` → commit history pills. |
| 9.3 | Type `git diff` | Chat | Plan: `git.diff` → color-coded diff output. |
| 9.4 | Type `git branch` | Chat | Plan: `git.branch` → branch list with current indicator (✓). |
| 9.5 | Type `git stash` | Chat | Plan: `git.stash` → stash saved. |
| 9.6 | Type `show recent commits` | Chat | Natural language → routes to `git.log`. |
| 9.7 | Type `what changed recently` | Chat | Natural language → routes to `git.diff`. |
| 9.8 | Type `list branches` | Chat | Natural language → routes to `git.branch`. |
| 9.9 | Type `git tag` | Chat | Plan: `git.tag` → lists tags. |

```bash
curl -X POST http://127.0.0.1:8100/run \
  -H "Content-Type: application/json" -d '{"input":"git status"}'
```

**Pass criteria:** All 13 git tools reachable. Natural language phrases route correctly. Branch displayed in status output.

---

## Act 10 — Workflow Composition DSL (24 Templates)

**Goal:** Test user-defined workflows with triggers and variables.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 10.1 | Click **Workflows** (Ctrl+5) | Nav | Workflow list. |
| 10.2 | Create a workflow with trigger | Composer | Name, triggers, steps, variables. |
| 10.3 | Type `run workflow <name>` | Chat | Workflow executes with variable substitution. |
| 10.4 | Check **24 built-in templates** | Terminal | `GET /workflow-templates` → 24 templates. |
| 10.5 | Enable/disable a workflow | Composer | Toggle persists. Disabled workflows skip trigger matching. |

```bash
curl http://127.0.0.1:8100/workflow-templates
curl http://127.0.0.1:8100/workflows
```

**Pass criteria:** Workflow CRUD works. Trigger matching fires. 24 templates available. Variable substitution works.

---

## Act 11 — Multi-Agent Coordination (6 Builtins + 21 Templates)

**Goal:** Test agent CRUD, delegation, orchestration, agent templates.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 11.1 | Click **Agents** (Ctrl+7) | Nav | 6 builtin agents: filesystem, git, shell, system, mcp, + any user-created. |
| 11.2 | Check **Agent Status Bar** | Top | Fleet summary: online/degraded/offline counts + top performer. |
| 11.3 | Click **From Template** | Agents | 21 agent blueprints including: code-reviewer, devops, project-navigator, security-auditor, release-manager, test-engineer, documentation-writer, ci-cd-specialist, performance-analyst, dependency-manager, infrastructure-scanner, onboarding-guide, debugger, refactorer, api-designer, docker-engineer, db-optimizer, frontend-analyst, sre-agent, changelog-writer, data-engineer. |
| 11.4 | Create agent from template (e.g. `debugger`) | Agents | Agent created with capabilities and tool_filter pre-filled. |
| 11.5 | Check **Orchestration** panel | Agents | Strategy selector, fallback attempts, pipeline toggle. |
| 11.6 | Type `delegate to filesystem list .` | Chat | Delegation → `filesystem.list` via filesystem agent. |
| 11.7 | Delete custom agent | Agents | Removed. Builtins cannot be deleted. |

```bash
# List all 21 agent blueprint templates
curl http://127.0.0.1:8100/agent-templates

# Create from template
curl -X POST http://127.0.0.1:8100/agents/from-template/sre-agent

# Agent summary
curl http://127.0.0.1:8100/agents/summary
```

**Pass criteria:** CRUD works, 21 templates create agents, delegation routes correctly, orchestration configurable.

---

## ⚡ How to Execute a Single Agent — Quick Reference

There are five ways to run an agent in Machina OS. Start with Method 1 for quick tests; use the others when you need more control or want to chain multiple agents together.

---

### Method 1 — Natural Language (Chat)

**Best for:** Quick one-off tasks. No setup needed.

Open the Neural Link chat and type a sentence like:

```
ask agent git to show status
use agent system for disk info
send to agent filesystem grep TODO in .
delegate to filesystem list .
```

**What happens behind the scenes:**
1. The intake parser recognises the delegation pattern and extracts the agent name (`git`, `system`, ...) and the task (`show status`, `disk info`, ...).
2. The planner looks up that agent in the pool, picks the right tool (`git.status`, `system.disk`, ...) and builds a one-step plan.
3. The executor runs the tool through that agent and displays the result in the chat.

You can see which agent handled the step in the **Agent Messages** sub-tab under Agents.

---

### Method 2 — Agent Task Queue (UI)

**Best for:** Sending a specific tool call to a known agent, then executing it on demand.

**Step 1 — Go to Agents view** (Ctrl+7) and find the **Agent Task Queue** in the Pipeline sub-panel.

**Step 2 — Fill in the form:**
- **Agent**: select one of the four built-in agents or any custom agent you created.
- **Tool**: type the tool name, e.g. `filesystem.list` or `git.status`.
- **Arguments**: JSON object, e.g. `{"path": "."}`.
- **Priority**: 1 (highest) to 5 (lowest).

**Step 3 — Click Enqueue.** The task appears in the queue with status **QUEUED**.

**Step 4 — Click ⚡ Auto-Execute** next to the task to run it immediately. The result appears inline. Click **Auto-Execute All** to drain all queued tasks for that agent at once.

---

### Method 3 — Smart Scheduling (UI)

**Best for:** When you know the tool you want to call but don't care which agent runs it — the system picks the best one automatically.

**Step 1 — Go to Agents view** (Ctrl+7) and scroll down to the **Smart Task Scheduling** panel.

**Step 2 — Select a tool** from the dropdown. It lists all 52 registered tools. When you pick one, the **Arguments** field auto-fills with the correct JSON for that tool. For example:
- Selecting `git.status` fills in `{"cwd":"."}`
- Selecting `filesystem.grep` fills in `{"path":".","query":"TODO"}`
- Selecting `system.info` fills in `{}`

Adjust the auto-filled values to match what you actually want.

**Step 3 — Click Schedule & Execute.** The system:
1. Scores every registered agent by their historical success rate with that tool.
2. Routes the task to the highest-scoring agent.
3. Executes the tool immediately.
4. Displays the full result in a green box below the form.

The response also tells you **which agent** was chosen (e.g. `agent_id: "filesystem"`) and the **confidence score** (0.0–1.0). If no agent has history with that tool, the default confidence is 0.5 and routing uses tool-filter pattern matching.

**Example walkthrough:**
1. Select `git.status` → args auto-fill to `{"cwd":"."}`
2. Click **Schedule & Execute**
3. Result box shows: `status: "SCHEDULED"`, `agent_id: "git"`, then the full git status output with branch, changed files, etc.

> **Troubleshooting:** If you see `FAILED` with a message like "missing required positional argument", it means the auto-filled arguments don't match the tool's parameter names. Check the tool's detail page (Tools view → click the tool) for the exact parameter names.

---

### Method 4 — Workflow Chain (UI / Studio)

**Best for:** Running multiple tools through multiple agents in sequence, where the output of one step feeds into the next.

> **Note:** The Workflow Studio (Ctrl+6) is a visual node-based editor covered in detail in Act 14 of this storyboard and in section 20 of the [Multi-Agent Manual](MULTI_AGENT_MANUAL.md). This method shows both the simple list-based editor and a brief Studio path. You don't need Studio experience — the list editor works fine for your first chain.

#### Option A — List Editor (no Studio needed)

**Step 1 — Go to Agents view** (Ctrl+7) → scroll to **Workflow Chains** panel → click the **+** button or expand the create form.

**Step 2 — Give the chain a name** (e.g. "Check project health") and optionally a description.

**Step 3 — Add steps one by one.** Each step needs:
- **Agent** — pick from the dropdown (e.g. `filesystem`, `git`, `system`).
- **Tool** — pick from the dropdown (e.g. `filesystem.tree`, `git.status`).
- **Description** — a short label shown in the chain card (e.g. "Get project tree").
- **Output key** — an identifier for this step's output (e.g. `tree_output`). Other steps can consume it.
- **Input from** — set this to a previous step's output key if you want its data piped in (e.g. `tree_output`).
- **Arguments** — JSON for the tool, e.g. `{"path":".","max_depth":2}`. In Studio, the smart argument builder auto-creates individual form fields — just fill them in instead of pasting JSON.

**Step 4 — Click Create.** The chain appears as a card with colored badges showing the data flow.

**Step 5 — Click Execute** on the card. Steps run in order. Each step's result feeds into the next via the output_key → input_from bridge. Results appear in the **Chain Execution History** panel below.

**Concrete example — a 4-step "Pre-Commit Health Check" chain:**

This chain automates a common developer workflow: before committing, check git status, scan for leftover TODOs, look for debug print statements, and verify disk space.

| Step | Agent | Tool | Output Key | Input From | Arguments |
|------|-------|------|------------|------------|-----------|
| 1 | git | git.status | git_state | — | `{"cwd":"."}` |
| 2 | filesystem | filesystem.grep | todo_hits | — | `{"query":"TODO\|FIXME","path":"."}` |
| 3 | filesystem | filesystem.grep | debug_prints | — | `{"query":"console\\.log\|print\\(","path":"."}` |
| 4 | system | system.disk | disk_check | — | `{"path":"."}` |

After execution, you'll see four green ✓ marks in the history. Step 1 shows your uncommitted changes, Step 2 reveals any TODO/FIXME items in the codebase, Step 3 catches leftover debug statements, and Step 4 confirms you have enough disk space. Use the **Debug** button (amber bug icon) to watch each step execute in real-time with live canvas node status updates.

> **Where are chains saved?** Workflow chains are persisted to SQLite (`chains.db`). They survive server restarts. When you create, update, rollback, or delete a chain, the change is automatically written to disk.

> **How does versioning work?** Every chain has a version number (starts at 1) and an internal version history. When you edit steps, drag a step between lanes, resolve conflicts, or apply optimization, the system saves a snapshot of the current state before applying changes and bumps the version number. To see past versions, click **History** on a chain card. To revert, click **Rollback** — this restores the old steps but saves the current state first, so rollback is non-destructive (you can always undo a rollback). Executing a chain does **not** change the version.

#### Option B — Visual Studio (drag-and-drop)

If you prefer a visual approach, open the **Studio** (Ctrl+6):

1. In the left palette, find the tools you want (use the filter box).
2. Drag each tool onto the canvas — a node appears.
3. Set the agent and arguments in the right-hand properties panel.
4. Connect nodes by dragging from one node's output port to the next node's input port. This auto-sets `input_from`.
5. Click **Save** → then **Execute**.

**Navigating large pipelines:** Use the mouse wheel to zoom in/out (zooms towards cursor). Click the **Fit View** button to auto-size the viewport to all nodes. Toggle **Pan mode** (hand icon) or hold Shift and drag to scroll the canvas. Zoom range: 15%–200%.

**Opening an existing chain:** Click the **Open** button (folder icon) in the Studio toolbar to see a list of all saved chains. Click one to load it into the visual editor.

**Debug Execution:** Click the **Debug** button (amber bug icon) to start an interactive stepping session:
- A debug toolbar appears with **Step Over**, **Continue**, and **Stop** buttons
- Click **Step Over** to execute one step at a time, or **Continue** to run all remaining steps
- Each node pulses **amber** while its step is running
- Turns **green ✓** on success, **red ✗** on failure, or **gray ⊘** if skipped
- The resizable results tray below the canvas shows incremental outputs with duration metrics (drag the top edge to resize)
- Click **Stop** to abort at any point
- Errors display inline with error codes

This is the recommended way to test and troubleshoot chains.

See **Act 14** for a full walkthrough of the Studio, and the [Multi-Agent Manual § 20](MULTI_AGENT_MANUAL.md) for advanced features like conditions and branching.

---

### Method 5 — From a Template (One-Click)

**Best for:** Running a pre-built multi-step workflow without building anything from scratch. Good for exploring what chains can do.

**Step 1 — Go to Agents view** (Ctrl+7) → **Workflow Chains** panel → click **Use Template**.

**Step 2 — Browse the 35 available templates.** Each card shows the name, description, and number of steps. Some useful starting points:
- `code-review` — scans project tree, git status, greps for patterns, reads key files (4 steps).
- `deploy-check` — git log, memory check, disk check (4 steps).
- `git-hygiene` — status, branches, stash, log, gitignore check (5 steps).
- `security-audit` — searches for secrets, insecure patterns, config files (4 steps).

**Step 3 — Click a template card.** A new chain is created instantly with all steps pre-configured and agents assigned.

**Step 4 — Click Execute** on the new chain card. Watch the steps run sequentially. Check the **Chain Execution History** panel for the results of each step.

**Step 5 (optional) — Click Auto-Assign** to let the system redistribute steps to agents based on capability scores. Click **Optimize** to auto-detect which steps can run in parallel. Then use **∥ Parallel** to execute with parallelism enabled.

---

### Which Method Should I Use?

| Situation | Use | Effort |
|-----------|-----|--------|
| Quick test — "what's the git status?" | **Method 1** — type in chat | Zero setup |
| Run one specific tool on one specific agent | **Method 2** — Agent Task Queue | Pick agent + tool |
| Run one tool, let the system pick the best agent | **Method 3** — Smart Scheduling | Pick tool only |
| Multi-step pipeline with manual control | **Method 4A** — List Editor | Add steps, wire output keys |
| Multi-step pipeline, visual wiring | **Method 4B** — Studio | Drag, connect, save |
| Pre-built pipeline, one click | **Method 5** — Template | Click template, click execute |

> **Tip:** Start with Method 1 or 5 to see agents in action. Move to Method 3 when you want more control over a single tool. Use Method 4 when you need multi-step chains with data flowing between agents.

---

## Act 12 — Agent Health & Performance

**Goal:** Test health monitoring, capability learning, reputation, performance dashboards.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 12.1 | Check **Agent Health** panel | Agents | Status per agent: ONLINE/DEGRADED/OFFLINE with error streaks, latency. |
| 12.2 | Execute filesystem/git commands | Chat | Generates capability learning data. |
| 12.3 | Check **Capability Learning** | Agents | Tool, success_rate, confidence, avg_duration, samples, last_error. |
| 12.4 | Check **Reputation** | Agents | Reputation score, success rate cards, tools used badges. |
| 12.5 | Check **Capability Discovery** | Agents | Discovered from filter (globs) + history (execution), confidence scores. |
| 12.6 | Check **Performance Dashboard** | Agents | All agents compared: reputation, success rate, latency. |
| 12.7 | Check **Performance Trends** | Agents | SVG dual-line chart (amber=reputation, green=success rate). |
| 12.8 | Check **Health History** | Agents | Check log with success/failure dots, latency, errors, timestamps. |

```bash
curl http://127.0.0.1:8100/agents/health
curl http://127.0.0.1:8100/agents/filesystem/performance
curl http://127.0.0.1:8100/agents/performance/comparison
curl http://127.0.0.1:8100/agents/filesystem/health/trends
```

**Pass criteria:** Health displays, capability data accumulates, performance dashboards render.

---

## Act 13 — Consensus & Negotiation

**Goal:** Test multi-agent consensus and agent-to-agent negotiation.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 13.1 | Create **consensus request** | Agents → Consensus | Question + candidates → PENDING. |
| 13.2 | Cast votes (APPROVE/REJECT) | Consensus | Votes recorded with optional reasons. |
| 13.3 | Click **Resolve** | Consensus | Strategy applied → RESOLVED or REJECTED. |
| 13.4 | Check **Consensus Patterns** | Agents | Tool patterns with approval rate, auto-skip indicator. |
| 13.5 | Create **negotiation** | Agents → Negotiations | Priority-based proposal → PROPOSED. |
| 13.6 | Click **Auto-Counter** | Negotiations | System picks best alternative by capability confidence. |
| 13.7 | Click **Accept** or **Auto-Resolve** | Negotiations | Winner determined. |

**Pass criteria:** Consensus lifecycle works. Negotiation flows through phases.

---

## Act 14 — Workflow Chains & Pipeline Wizard (35 Templates)

**Goal:** Test multi-agent workflow chains with the visual pipeline editor.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 14.1 | Check **Workflow Chains** panel | Agents | Chain list + create form. |
| 14.2 | Click **Use Template** | Template picker | 35 templates including: code-review, deploy-check, project-scan, security-audit, dependency-check, release-readiness, onboarding-scan, log-investigation, cleanup-sweep, test-suite-check, api-health-check, documentation-audit, migration-check, ci-cd-audit, performance-profile, git-hygiene, env-config-audit, code-quality-scan, error-investigation, license-compliance, code-review-deep, debug-investigation, refactoring-analysis, api-design-review, security-deep-scan, docker-k8s-review, test-coverage-analysis, documentation-review, db-optimization, hotfix-workflow, pr-readiness-check, changelog-generation, monorepo-scan, stale-branch-cleanup, feature-branch-setup. |
| 14.3 | Create chain with **Pipeline Wizard** | Editor | Steps with drag handles, all AgentWorkflowStep fields editable: description, output_key, input_from, arguments (smart form or JSON), condition, branch_to, parallel_group. |
| 14.4 | Click **Auto-Assign Agents** | Editor | Pipeline negotiation assigns best agents. |
| 14.5 | Click **Execute** on a chain | Cards | Sequential execution with output bridging. |
| 14.6 | Click **∥ Parallel** | Cards | Steps grouped by parallel_group run concurrently. |
| 14.7 | Click **Optimize** | Cards | Dependency analysis creates parallel groups. |
| 14.8 | Click **Studio** button on a chain card | Cards | Opens chain in **Workflow Studio** visual editor. |
| 14.9 | Check **Execution History** | Agents | Records with SUCCESS/PARTIAL/FAILED, step counts (✓✗⊘). |
| 14.10 | Click **Replay** | History | Re-runs chain with optional argument overrides. |
| 14.11 | Check **versioning** | Cards | History → version list. Rollback → reverts. |

```bash
# List all 35 chain templates
curl http://127.0.0.1:8100/workflow-chain-templates

# Create from template
curl -X POST http://127.0.0.1:8100/workflow-chains/from-template/hotfix-workflow

# Execute
curl -X POST http://127.0.0.1:8100/workflow-chains/<id>/execute

# Parallel execute
curl -X POST http://127.0.0.1:8100/workflow-chains/<id>/execute-parallel

# Optimize
curl -X POST http://127.0.0.1:8100/workflow-chains/<id>/optimize

# Auto-assign
curl -X POST http://127.0.0.1:8100/workflow-chains/<id>/auto-assign
```

**Pass criteria:** 35 templates available. Chain CRUD, execution, optimization, versioning, replay, Studio editing all work.

---

## Act 15 — Workflow Studio (Visual Editor)

**Goal:** Test the node-based visual workflow composer with smart argument builder.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 15.1 | Click **Studio** nav tab (Ctrl+6) | Nav | Three-panel layout: palette (left), SVG canvas (center), properties (right). |
| 15.2 | Check **palette tabs** | Left panel | Three tabs: Tools (grouped by category), Agents (with tool count), Templates (chain + DSL). |
| 15.3 | Filter palette | Search input | Type "git" → filters to git tools only. |
| 15.4 | **Drag a tool** from palette onto canvas | Canvas | Node appears at drop position with tool name, ports, agent label. |
| 15.5 | **Drag an agent** from palette | Canvas | Agent node appears (placeholder for agent-scoped steps). |
| 15.6 | **Double-click** empty canvas | Canvas | Empty node created at click position. |
| 15.7 | **Select a node** | Canvas | Node highlights with ring. Properties panel populates. |
| 15.8 | Edit node via **smart argument builder** | Properties | Dynamic form fields per tool (text, number, checkbox, dropdown) instead of raw JSON. Toggle JSON/Form mode. Tool description shown below tool dropdown. |
| 15.9 | Check **tooltip icons** (ℹ️) | Properties | Every property field has an info icon with contextual help. |
| 15.10 | Check **Data Flow** section | Properties | Output Key and Input From with clickable suggestions from other nodes. |
| 15.11 | Check **Advanced Options** (collapsible) | Properties | Condition, Branch To, Parallel Group under expandable section. |
| 15.12 | Click **?** help button | Properties sidebar | Collapsible inline help guide with 5 sections: Getting Started, Data Flow, Arguments, Advanced Features, Keyboard Shortcuts. |
| 15.13 | **Draw an edge**: click output port → drag to input port | Canvas | Cubic Bezier SVG path. Temp dashed line previews during drag. Auto-sets input_from. |
| 15.14 | **Move a node** by dragging | Canvas | Node repositions. Edges update in real-time. |
| 15.15 | Press **Delete** key | Canvas | Selected node removed. Connected edges cleaned up. |
| 15.16 | Click a **chain template** in Templates tab | Palette | Template loads into canvas: sequential nodes auto-positioned, auto-connected with edges. |
| 15.17 | Enter a name and click **Save** | Toolbar | `POST /workflow-chains` → chain saved. Toast confirms. |
| 15.18 | Click **Execute** | Toolbar | Saves first if needed → `POST /workflow-chains/{id}/execute` → result toast. |
| 15.19 | Click **Auto-Assign** | Toolbar | Saves → `POST /auto-assign` → nodes update with assigned agents. |
| 15.20 | Click **Optimize** | Toolbar | Saves → `POST /apply-optimization` → parallel groups added. |
| 15.21 | Load an existing chain via **Studio button** on chain card | Chain cards | Chain loaded into Studio bidirectionally. Edit and save back. |

**Pass criteria:** Full visual workflow authoring with smart form builder, tooltips, inline help, data flow suggestions, save/execute/auto-assign/optimize, bidirectional chain loading.

---

## Act 16 — Agent Communication

**Goal:** Test agent-to-agent communication: requests, broadcasts, handoffs, collaborations, task queues.

**Background:** Machina OS agents communicate through 6 distinct channels on the AgentBus. These protocols fire automatically during multi-agent plan execution (e.g., negotiations when multiple agents match a tool, handoffs when an agent is degraded, broadcast queries for consensus voting). The panels below let you inspect and manually trigger these interactions for testing.

| Channel | What it does | Lifecycle |
|---------|-------------|----------|
| Requests | Agent A asks Agent B directly | PENDING → DELIVERED → RESPONDED |
| Broadcasts | One agent polls many, collects answers | PENDING → COLLECTING → COMPLETED/EXPIRED |
| Negotiations | Two agents bid on tool ownership | PROPOSED → COUNTERED → ACCEPTED/RESOLVED |
| Handoffs | Formal task transfer between agents | REQUESTED → ACCEPTED → EXECUTING → COMPLETED |
| Collaborations | Shared session with common context | create → join → set_context → close |
| Task Queue | Priority-sorted work items per agent | QUEUED → RUNNING → COMPLETED/FAILED |

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 16.1 | Create **Agent Request** | Agents → Requests | from_agent, to_agent, action → PENDING. |
| 16.2 | Click **Respond** | Requests | Response submitted → RESPONDED. |
| 16.3 | Create **Broadcast Query** | Agents → Broadcasts | from_agent, question, targets, optional timeout → sent. |
| 16.4 | Click **Aggregate** on completed query | Broadcasts | Strategy result (ALL/FIRST/MERGE/MAJORITY). |
| 16.5 | Create **Handoff** | Agents → Handoffs | from → to → REQUESTED → Accept → EXECUTING → Complete. |
| 16.6 | Create **Collaboration Session** | Agents → Collaborations | task_id, participants → session. Join, set context, close. |
| 16.7 | Enqueue **Agent Task** | Agents → Task Queue | agent_id, tool, priority → QUEUED. |
| 16.8 | Click **⚡ Auto-Execute** | Task Queue | Tool invoked via registry → result displayed. |
| 16.9 | Click **Auto-Execute All** | Task Queue | Drains all QUEUED in priority order. |
| 16.10 | Toggle **Flat/Threads** in message log | Agents | Threaded view groups by correlation_id. |

**Pass criteria:** All communication channels work. Task queue auto-executes. Threading groups conversations.

---

## Act 17 — Communications Dashboard & Pipeline Lanes

**Goal:** Test SVG communication graph, activity feed, negotiation timeline, pipeline lanes.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 17.1 | Click **Communications** sub-tab | Agents | Stats cards + SVG graph + activity feed. |
| 17.2 | Check **Communication Graph** | Communications | Circular layout. Color-coded edges: cyan=request, amber=negotiation, purple=handoff, emerald=broadcast. |
| 17.3 | Use **type filter** on activity feed | Communications | Filters to specific event type. |
| 17.4 | Select negotiation in **Timeline** dropdown | Communications | Vertical timeline: phase-colored dots, round numbers, agent labels, reasons. |
| 17.5 | Check **Pipeline Lane View** | Pipelines sub-tab | Agent lanes with draggable steps, color-coded. |
| 17.6 | **Drag step** between lanes | Pipeline lanes | Visual feedback. Step reassigned. Version increments. |
| 17.7 | Click **Negotiate All** | Chains panel | Bulk negotiation across all chains. |
| 17.8 | **Resolve conflicts** after negotiation | Conflict picker | Radio buttons for tied agents per step. |
| 17.9 | Click **New from Lanes** | Pipelines | Lane Builder: tool palette + agent lanes → create chain visually. |

**Pass criteria:** Graph renders, feed filterable, lanes support drag-drop, conflicts resolvable.

---

## Act 18 — Security Center

**Goal:** Test the dedicated Security Center UI view and its four sub-tabs: AES-256-GCM encrypted secrets, SOC 2 audit log with hash chain verification, static vulnerability analysis with CWE IDs, and credential scrubbing with 21 regex patterns.

> **Security Center** is the 15th UI view. Navigate to it directly or press Ctrl+K and type "security".

### Concepts

The Security Center bundles four independent modules:

| Module | What It Does | Key Detail |
|--------|-------------|------------|
| **Secrets Vault** | Encrypt and store secrets at rest using AES-256-GCM with PBKDF2 key derivation (600 000 iterations). Per-secret random nonces. | Values are never returned in list endpoints — only names. Retrieve requires an explicit GET by name. |
| **Audit Log** | Immutable event ledger for every security-sensitive action. Each entry is linked to the previous by a SHA-256 hash chain: `chain_hash = SHA-256(prev_hash : audit_id : timestamp)`. | Tampering with or deleting any row breaks the chain. `verify_chain()` walks entries in insertion order and reports breaks. Genesis hash is 64 zeros. |
| **Vulnerability Scanner** | Static code analysis against 14 regex patterns covering 8 CWE categories (SQL injection, XSS, SSRF, command injection, hardcoded secrets, insecure deserialization, path traversal, eval/exec). | Comment lines are auto-skipped. Each finding includes CWE ID, severity (CRITICAL/HIGH/MEDIUM/LOW), matched code snippet, line number, and a fix recommendation. |
| **Credential Scrubber** | Regex-based redaction with 21 built-in patterns: OpenAI/Anthropic/GitHub/GitLab/Slack/Google/AWS/Azure keys, JWTs, Bearer tokens, PEM private keys, connection strings, generic password/token values. | Also wired internally — `scrub_text()` and `scrub_output()` sanitise logs and API responses system-wide, not just in the UI tool. |

**Self-reinforcing audit trail:** every secret access and code scan automatically creates an audit entry — the trail tracks who used the security tools and when.

### Test Steps

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 18.1 | Store a secret | Secrets Vault sub-tab or terminal | `POST /security/secrets` with `{"name":"demo_key","value":"sk-proj-abc123"}` → stored, encrypted at rest with AES-256-GCM. |
| 18.2 | List secrets | Secrets Vault sub-tab or terminal | `GET /security/secrets` → names only (values never in list response). |
| 18.3 | Retrieve a secret | Secrets Vault sub-tab or terminal | `GET /security/secrets/demo_key` → decrypted value returned. An audit entry is recorded. |
| 18.4 | Delete a secret | Secrets Vault sub-tab or terminal | `DELETE /security/secrets/demo_key` → removed. An audit entry is recorded. |
| 18.5 | Scan code for vulnerabilities | Vuln Scanner sub-tab | Paste Python code with `cursor.execute(f"SELECT * FROM users WHERE id={user_input}")` → finding: SQL Injection (CWE-89), CRITICAL, with line number, snippet, and recommendation to use parameterised queries. |
| 18.6 | Scan code with multiple issues | Vuln Scanner sub-tab | Paste code with `os.system(f"rm {path}")` + `pickle.load(data)` → two findings: Command Injection (CWE-78, CRITICAL) + Insecure Deserialization (CWE-502, CRITICAL). |
| 18.7 | Check audit log | Audit Log sub-tab | Summary cards show total entries, counts by risk level (LOW/MEDIUM/HIGH/CRITICAL). Entry list shows recent actions with outcome badges. |
| 18.8 | Verify hash chain integrity | Audit Log sub-tab | Click **Verify Chain** → `{valid: true, checked: N, breaks: []}`. If any entry had been tampered with, `breaks` would contain the mismatched entry IDs. |
| 18.9 | Export audit log | Audit Log sub-tab | Click **Export JSON** → downloads `machina_audit_log.json` with up to 10 000 entries including all fields and chain hashes. |
| 18.10 | Scrub credentials from text | Scrubber sub-tab | Paste text containing `sk-proj-abc123def456`, `ghp_A1B2C3D4E5F6...`, `eyJhbGciOi...` → output shows `[REDACTED_API_KEY]`, `[REDACTED_GITHUB_PAT]`, `[REDACTED_JWT]` respectively. |
| 18.11 | Scrub connection strings | Scrubber sub-tab | Paste `postgres://admin:pass@db.host/mydb` → `[REDACTED_CONN_STRING]`. |

### Terminal Examples

```bash
# Store a secret
curl -X POST http://127.0.0.1:8100/security/secrets \
  -H "Content-Type: application/json" -d '{"name":"demo_key","value":"sk-proj-abc123"}'

# Retrieve (decrypted)
curl http://127.0.0.1:8100/security/secrets/demo_key

# Analyze code — SQL injection example
curl -X POST http://127.0.0.1:8100/security/analyze \
  -H "Content-Type: application/json" \
  -d '{"content": "query = \"SELECT * FROM users WHERE id=\" + user_input\ncursor.execute(query)", "file_path": "app.py"}'

# Analyze code — multiple findings
curl -X POST http://127.0.0.1:8100/security/analyze \
  -H "Content-Type: application/json" \
  -d '{"content": "import os, pickle\nos.system(f\"rm {path}\")\ndata = pickle.load(open(f))", "file_path": "danger.py"}'

# Audit log summary
curl http://127.0.0.1:8100/security/audit/summary

# Verify chain integrity
curl http://127.0.0.1:8100/security/audit/verify

# Export full audit log
curl http://127.0.0.1:8100/security/audit/export -o machina_audit_log.json

# Scrub credentials
curl -X POST http://127.0.0.1:8100/security/scrub \
  -H "Content-Type: application/json" \
  -d '{"text": "key=sk-proj-abc123def456 token=ghp_A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q7R8 jwt=eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.abc conn=postgres://admin:secret@db.host/mydb"}'
```

**Pass criteria:** Security Center view loads with all 4 sub-tabs functional. Secrets stored and retrieved encrypted (AES-256-GCM). Vulnerability scanner detects SQL injection and command injection with correct CWE IDs. Audit chain is valid with zero breaks. Scrubber redacts API keys, JWTs, GitHub tokens, and connection strings. Every secret access generates an audit entry.

---

## Act 19 — MCP Protocol (Client + Provider)

**Goal:** Test the full MCP Protocol system — both as a **client** consuming external MCP servers, and as a **provider/server** exposing MachinaOS capabilities to external clients (Claude Desktop, Cursor, etc.).

> **MCP** is the 16th UI view. Four sub-tabs: Server Registry, Discovered Tools, Resources, Prompts.
> See also: [machinaos_mcp_manual.md](machinaos_mcp_manual.md) for dedicated MCP walkthrough.

### 19-A: Default MCP Servers & Auto-Connect

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 19.1 | List MCP servers | Terminal | `GET /mcp/servers` → 5 pre-configured servers: sequential-thinking ✅, memory ✅, fetch ✅, github ❌, sqlite ❌. |
| 19.2 | Check auto-connected servers | Terminal | `GET /mcp/tools` → tools from auto-connected servers (if npx available). |
| 19.3 | Verify MCP UI → Server Registry | MCP view | 5 servers listed with status indicators. Connected servers show green dot. |

```bash
# List all pre-configured servers
curl http://127.0.0.1:8100/mcp/servers

# List discovered tools from auto-connected servers
curl http://127.0.0.1:8100/mcp/tools
```

### 19-B: MCP Client — Server Management

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 19.4 | Register a custom MCP server | Terminal | `POST /mcp/servers` with name, command, args → server config saved. |
| 19.5 | Connect to server | Terminal | `POST /mcp/servers/{id}/connect` → connection established, tools discovered. |
| 19.6 | List MCP tools | Terminal | `GET /mcp/tools` → discovered tools with `mcp.<server>.<tool>` namespace. |
| 19.7 | List MCP resources | Terminal | `GET /mcp/resources` → resources grouped by server. |
| 19.8 | Read a resource | Terminal | `POST /mcp/resources/read` → resource content. |
| 19.9 | List MCP prompts | Terminal | `GET /mcp/prompts` → prompt templates by server. |
| 19.10 | Resolve a prompt | Terminal | `POST /mcp/prompts/get` → prompt with argument substitution. |
| 19.11 | Disconnect server | Terminal | `POST /mcp/servers/{id}/disconnect` → clean shutdown. |
| 19.12 | Delete server config | Terminal | `DELETE /mcp/servers/{id}` → removed from registry. |

```bash
# Register an MCP server (e.g. filesystem server)
curl -X POST http://127.0.0.1:8100/mcp/servers \
  -H "Content-Type: application/json" \
  -d '{"name":"demo-server","command":"npx","args":["-y","@modelcontextprotocol/server-filesystem","./"]}'

# Connect (discovers tools + resources + prompts)
curl -X POST http://127.0.0.1:8100/mcp/servers/<id>/connect

# List discovered MCP tools
curl http://127.0.0.1:8100/mcp/tools

# Resources (grouped by server)
curl http://127.0.0.1:8100/mcp/resources

# Flat resource list
curl http://127.0.0.1:8100/mcp/resources/flat

# Read a resource
curl -X POST http://127.0.0.1:8100/mcp/resources/read \
  -H "Content-Type: application/json" -d '{"server":"demo-server","uri":"file:///README.md"}'

# Prompts
curl http://127.0.0.1:8100/mcp/prompts
curl http://127.0.0.1:8100/mcp/prompts/flat

# Resolve a prompt
curl -X POST http://127.0.0.1:8100/mcp/prompts/get \
  -H "Content-Type: application/json" -d '{"server":"demo-server","name":"example","arguments":{}}'
```

### 19-C: MCP Provider — MachinaOS as MCP Server

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 19.13 | Check MCP serve status | Terminal | `GET /mcp/serve/status` → session count, tool count (52+ native + 4 virtual), resource count (17), prompt count (4). |
| 19.14 | Open SSE connection | Terminal | `GET /mcp/serve/sse` → SSE stream with `session_id` event, then keepalives every 30s. |
| 19.15 | Initialize MCP session | Terminal | `POST /mcp/serve/messages?session_id=X` with `initialize` → capabilities + protocol_version `2024-11-05`. |
| 19.16 | List tools via MCP | Terminal | `POST /mcp/serve/messages?session_id=X` with `tools/list` → all Machina tools + 4 virtual tools. |
| 19.17 | Call a tool via MCP | Terminal | `POST /mcp/serve/messages?session_id=X` with `tools/call` → tool executes, result returned. |
| 19.18 | List resources via MCP | Terminal | `POST /mcp/serve/messages?session_id=X` with `resources/list` → 17 resources across 7 domains. |
| 19.19 | Read a resource via MCP | Terminal | `POST /mcp/serve/messages?session_id=X` with `resources/read` → resource content. |
| 19.20 | List prompts via MCP | Terminal | `POST /mcp/serve/messages?session_id=X` with `prompts/list` → 4 templates. |
| 19.21 | Resolve a prompt via MCP | Terminal | `POST /mcp/serve/messages?session_id=X` with `prompts/get` → resolved template. |
| 19.22 | Test virtual tool: `machina.create_task` | Terminal | Submit a goal → task created, returns task_id and status. |
| 19.23 | Test virtual tool: `machina.chat` | Terminal | Send message → conversational response. |
| 19.24 | Ping | Terminal | `POST /mcp/serve/messages?session_id=X` with `ping` → empty response (keepalive). |

```bash
# Check provider status
curl http://127.0.0.1:8100/mcp/serve/status

# Open SSE stream (use curl streaming or a browser EventSource)
curl -N http://127.0.0.1:8100/mcp/serve/sse

# Initialize (replace SESSION_ID with the session_id from the SSE endpoint event)
curl -X POST "http://127.0.0.1:8100/mcp/serve/messages?session_id=SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"demo","version":"1.0"}}}'

# List tools
curl -X POST "http://127.0.0.1:8100/mcp/serve/messages?session_id=SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'

# Call a tool (filesystem.list)
curl -X POST "http://127.0.0.1:8100/mcp/serve/messages?session_id=SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"filesystem.list","arguments":{"path":"."}}}'

# Call virtual tool (machina.create_task)
curl -X POST "http://127.0.0.1:8100/mcp/serve/messages?session_id=SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"machina.create_task","arguments":{"goal":"list files in current directory"}}}'

# Call virtual tool (machina.chat)
curl -X POST "http://127.0.0.1:8100/mcp/serve/messages?session_id=SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"machina.chat","arguments":{"message":"What is this project about?"}}}'

# List resources (17)
curl -X POST "http://127.0.0.1:8100/mcp/serve/messages?session_id=SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":6,"method":"resources/list","params":{}}'

# Read a resource
curl -X POST "http://127.0.0.1:8100/mcp/serve/messages?session_id=SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":7,"method":"resources/read","params":{"uri":"machina://workspace/languages"}}'

# List prompts (4)
curl -X POST "http://127.0.0.1:8100/mcp/serve/messages?session_id=SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":8,"method":"prompts/list","params":{}}'

# Resolve a prompt
curl -X POST "http://127.0.0.1:8100/mcp/serve/messages?session_id=SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":9,"method":"prompts/get","params":{"name":"analyze_code","arguments":{"code":"eval(user_input)"}}}'
```

### 19-D: MCP-Aware Planner

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 19.25 | Type `mcp.sequential-thinking.think` in chat | Chat | Detected as `mcp_tool` intent → plan with `requires_approval: true`. |
| 19.26 | Verify MCP agent in pool | Terminal | `GET /agents/summary` → includes `agent_mcp` in fleet count. |

### 19-E: MCP UI View

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 19.27 | Check **Server Registry** sub-tab | MCP view | 5 pre-configured servers, connect/disconnect buttons, register new button. |
| 19.28 | Check **Discovered Tools** sub-tab | MCP view | Tools grid with tool name, params, risk level, server source. |
| 19.29 | Check **Resources** sub-tab | MCP view | Resource list by server. Discover button. Read with content display. |
| 19.30 | Check **Prompts** sub-tab | MCP view | Prompt templates with argument badges. Resolve with argument inputs. |

**Pass criteria:** 5 default servers present. Auto-connect discovers tools. MCP Provider exposes 52+ tools + 4 virtual + 17 resources + 4 prompts via SSE. External clients can initialize, list, call, and read. MCP UI has 4 functional sub-tabs. MCP planner routes `mcp.*` tools with approval. agent_mcp in fleet.

---

## Act 20 — LLM Provider Configuration (7 Providers)

**Goal:** Test multi-provider LLM configuration, hot-reconfigure, and diagnostics.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 20.1 | Check LLM status | Terminal | `GET /llm/status` → provider, model, available, has_api_key, detail. |
| 20.2 | Check Settings UI → LLM panel | Settings | 6-provider LLM dropdown: Ollama, OpenAI, Gemini, Claude, OpenRouter, LM Studio. (GitHub Copilot moved to dedicated GitHub Connection panel.) |
| 20.3 | Select a provider | Settings | URL auto-fills from defaults. API key placeholder updates per provider. |
| 20.4 | Click **Test Connection** | Settings | `GET /llm/test` → connection status dot (green=OK, red=error with reason). |
| 20.5 | Refresh model list | Settings | Model dropdown populates from provider. |
| 20.6 | Switch provider at runtime | Settings | `POST /llm/config` → hot-reconfigure without restart. |
| 20.7 | Check **status bar LLM dot** | Bottom bar | Green dot + provider name when connected. Red when offline. |

```bash
# Current status with diagnostics
curl http://127.0.0.1:8100/llm/status

# Test connectivity
curl http://127.0.0.1:8100/llm/test

# Switch to OpenAI
curl -X POST http://127.0.0.1:8100/llm/config \
  -H "Content-Type: application/json" \
  -d '{"provider":"openai","base_url":"https://api.openai.com/v1","model":"gpt-4o","api_key":"sk-..."}'

# List available providers
curl http://127.0.0.1:8100/llm/providers
```

**Pass criteria:** All 6 LLM providers selectable in dropdown. GitHub Copilot available in GitHub Connection panel. Hot-reconfigure works. Diagnostics show specific error reasons (not running, auth error, timeout).

---

## Act 21 — Metrics & Observability

**Goal:** Test Metrics dashboard, Event Inspector, telemetry.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 21.1 | Click **Metrics** | Nav | 4 cards (success rate, avg steps, duration, events), SVG bar chart, tool table, errors. |
| 21.2 | Click **Events** | Nav | Filter bar (type/source/severity), paginated table, severity badges. |
| 21.3 | Filter by severity=ERROR | Events | Shows only errors. |
| 21.4 | Click **Settings** | Nav | System info, LLM settings (7 providers), personality, preferences, RAG status. |

```bash
curl http://127.0.0.1:8100/metrics/dashboard
curl "http://127.0.0.1:8100/events/query?severity=ERROR&limit=10"
curl http://127.0.0.1:8100/events/meta
```

**Pass criteria:** Metrics render with real data. Events filterable. Settings display system info.

---

## Act 22 — Real-Time Events & WebSocket

**Goal:** Verify live event push and notifications.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 22.1 | Open DevTools → Network → WS | Browser | WebSocket to `/ws` active. Heartbeat every ~30s. |
| 22.2 | Execute a command from another tab | Second tab | Live sidebar updates with events (step_started, step_succeeded). |
| 22.3 | Check bell after task completes | Top bar | Badge increments. Toast notification. |

**Pass criteria:** Events propagate live. Notifications fire.

---

## Act 23 — RAG & Semantic Search

> **Skip if chromadb not installed.** System degrades gracefully.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 23.1 | Index workspace | Terminal | `POST /rag/index` → chunk count. |
| 23.2 | Semantic search | Terminal | `POST /rag/search` → ranked code snippets. |
| 23.3 | Ask code question in chat | Chat | Response includes relevant indexed context. |
| 23.4 | Check RAG status in Settings | Settings | Active/available/unavailable state. Collection count if active. |

```bash
curl -X POST http://127.0.0.1:8100/rag/index \
  -H "Content-Type: application/json" \
  -d '{"path": ".", "workspace_id": "machina"}'

curl -X POST http://127.0.0.1:8100/rag/search \
  -H "Content-Type: application/json" \
  -d '{"query": "how does the planner work", "workspace_id": "machina"}'
```

**Pass criteria:** Indexing creates chunks, search returns relevant results. Settings show correct RAG state.

---

## Act 24 — Demo Mode

**Goal:** Test the 3-tier demo mode system.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 24.1 | `curl http://127.0.0.1:8100/demo/status` | Terminal | Returns current mode (INTERNAL/REVIEWER/DEMO). |
| 24.2 | Switch to DEMO mode | Terminal | `PUT /demo/mode` with `{"mode": "DEMO"}`. |
| 24.3 | Verify tool gating | Chat | Only 17 read-only tools available. Write/delete/shell blocked. |
| 24.4 | Seed demo workspace | Terminal | `POST /demo/seed` → 12-file "Acme Web Platform" sample project. |
| 24.5 | Check **guided prompts** | UI | 8 curated prompts appear in quick-prompts bar. |
| 24.6 | Check simplified nav | UI | Only 6 views visible: Home, Chat, Tools, Explorer, Agents, Settings. |
| 24.7 | Switch back to INTERNAL | Terminal | `PUT /demo/mode` with `{"mode": "INTERNAL"}`. Full access restored. |

```bash
curl -X PUT http://127.0.0.1:8100/demo/mode \
  -H "Content-Type: application/json" -d '{"mode": "DEMO"}'

curl -X POST http://127.0.0.1:8100/demo/seed
curl http://127.0.0.1:8100/demo/guided-prompts

curl -X PUT http://127.0.0.1:8100/demo/mode \
  -H "Content-Type: application/json" -d '{"mode": "INTERNAL"}'
```

**Pass criteria:** Mode switching works. Tool gating enforced. Seed workspace created. Guided prompts display.

---

## Act 25 — Desktop Shell (Tauri)

**Goal:** Verify the native desktop application.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 25.1 | Launch `machina-os-desktop.exe` | Desktop | Glassmorphic loading screen with orb animation. Backend auto-spawns. |
| 25.2 | Wait for backend | Desktop | Health check passes → UI loads in webview. |
| 25.3 | Check **frameless chrome** | Window | Custom titlebar with drag region, minimize/maximize/close buttons. |
| 25.4 | Check **system tray** | Tray | Icon with Show/Quit menu. Close → minimizes to tray. |
| 25.5 | Execute a command | Desktop UI | Same as browser UI — full functionality. |
| 25.6 | Check auto-updater | Desktop | (If configured) update banner appears when new version available. |
| 25.7 | Verify **source auto-sync** | Build | `npx tauri build` auto-runs `bundle_python.py --source-only` via `beforeBuildCommand` — ensures latest source is always bundled. |

**Pass criteria:** Desktop launches, spawns backend, renders UI, tray works, frameless chrome functions, builds always include latest source.

---

## Act 26 — Background Execution & LLM Config

**Goal:** Test background task runner and LLM reconfiguration.

```bash
curl -X POST http://127.0.0.1:8100/background/start
curl -X POST http://127.0.0.1:8100/background/submit \
  -H "Content-Type: application/json" -d '{"goal": "list ."}'
curl http://127.0.0.1:8100/background/status
curl -X POST http://127.0.0.1:8100/background/stop
```

**Pass criteria:** Background tasks queue+complete. LLM switchable at runtime with diagnostic detail.

---

## Act 27 — Stress Test

**Goal:** Run 5 concurrent commands.

```bash
curl -X POST http://127.0.0.1:8100/run -H "Content-Type: application/json" -d '{"input":"list ."}'
curl -X POST http://127.0.0.1:8100/run -H "Content-Type: application/json" -d '{"input":"read pyproject.toml"}'
curl -X POST http://127.0.0.1:8100/run -H "Content-Type: application/json" -d '{"input":"git status"}'
curl -X POST http://127.0.0.1:8100/run -H "Content-Type: application/json" -d '{"input":"list apps"}'
curl -X POST http://127.0.0.1:8100/run -H "Content-Type: application/json" -d '{"input":"system info"}'
```

| # | Expected |
|---|----------|
| 27.1 | All 5 return valid JSON with status `completed`. |
| 27.2 | No crashes or deadlocks. |
| 27.3 | `/tasks` lists all 5. |
| 27.4 | `/metrics` plan count +5. |
| 27.5 | Status bar shows accurate active count during execution. |

**Pass criteria:** Concurrent requests handled without errors.

---

## Act 28 — Context Directory

**Goal:** Set the active project context and verify agents operate within it.

| # | Action | Where | Expected Result |
|---|--------|-------|---------------|
| 28.1 | Check context pill in chat bar | Neural Link | Grey pill shows current path (e.g., `~/projects/machina-os`) or empty if unset. |
| 28.2 | Click the context pill | Chat bar | Context Picker modal opens. Current path + breadcrumb navigation. |
| 28.3 | View **Git Repos** section | Picker | Scanner finds git repos in parent directories and lists them. |
| 28.4 | Click a repo to select it | Picker | Pill updates to new path. Modal closes. |
| 28.5 | Check context via API | Terminal | `GET /context/dir` → `{"path": "/selected/path"}`. |
| 28.6 | Set context via API | Terminal | `PUT /context/dir` with `{"path": "."}` → confirmed. |
| 28.7 | Run `list files` after setting context | Chat | `filesystem.list` resolves against context dir, not CWD. |
| 28.8 | Restart server and check context | Terminal | `GET /context/dir` → context persists (saved in preferences). |

```bash
curl http://127.0.0.1:8100/context/dir
curl -X PUT http://127.0.0.1:8100/context/dir \
  -H "Content-Type: application/json" -d '{"path": "/home/user/my-project"}'
```

**Pass criteria:** Picker scans git repos, context saves/restores across restarts, agents resolve paths against context.

---

## Act 29 — Neural Link UI Enhancements

**Goal:** Test the smart typeahead and the done-panel collapsed view.

| # | Action | Where | Expected Result |
|---|--------|-------|---------------|
| 29.1 | Type `git` in chat input | Neural Link | Typeahead dropdown appears with git-related suggestions. |
| 29.2 | Press **↑/↓** arrows | Typeahead | Highlights suggestions without modifying input text. |
| 29.3 | Press **Enter** on highlighted item | Typeahead | Suggestion fills input **and sends** immediately (single keystroke). |
| 29.4 | Click a suggestion with mouse | Typeahead | Pick-and-send in one click (no double-click needed). |
| 29.5 | Type `vscode` | Typeahead | VS Code tool suggestions appear. |
| 29.6 | Type `secu` | Typeahead | Security-related suggestions appear. |
| 29.7 | Press **Escape** | Typeahead | Dropdown dismisses. |
| 29.8 | Execute any command | Chat | Completed plan card shows **COMPLETED** badge + `N/N steps — done` + inline result snippet (properly formatted, not raw JSON). |
| 29.9 | Click `▸ steps` on done card | Card | Full step list expands below. Click `▴ hide` to collapse. |
| 29.10 | Type `show recent commits` | Chat | Automatically routes to `git.log` (natural-language git detection). |
| 29.11 | Type `what changed recently` | Chat | Routes to `git.diff`. |
| 29.12 | Type `list branches` | Chat | Routes to `git.branch`. |

**Pass criteria:** Typeahead shows correct categories, pick-and-send works in one step, done cards show formatted result inline, natural-language git phrases route correctly.

---

## Act 30 — GitHub Integration

**Goal:** Test the full GitHub integration — PAT connection, in-UI Explorer, 7 GitHub tools, and intent-routed chat commands.

### 30-A: Connect & Status

| # | Action | Where | Expected Result |
|---|--------|-------|---------------|
| 30.1 | Open **Settings** → **GitHub Connection** section | Settings | PAT input field, Connect/Test/Disconnect buttons, status dot. |
| 30.2 | Enter a GitHub PAT and click **Connect** | Settings | `POST /github/config` → status dot turns green, username + avatar displayed. GitHub Explorer section appears below. |
| 30.3 | Click **Test** | Settings | `GET /github/test` → validates token against `api.github.com/user`. Shows `connected: true, username`. |
| 30.4 | Check **status bar** | Bottom bar | GitHub dot = green with authenticated username. |
| 30.5 | Verify LLM dropdown unchanged | Settings → LLM | GitHub Copilot NOT in LLM dropdown. LLM has 6 providers (Ollama, OpenAI, Gemini, Claude, OpenRouter, LM Studio). |

### 30-B: GitHub Explorer (in-UI)

| # | Action | Where | Expected Result |
|---|--------|-------|---------------|
| 30.6 | Click **Browse Repos** in GitHub Explorer | Settings | `GET /github/repos` → repo cards rendered (name, language dot, privacy badge, ⭐/forks/issues counts). |
| 30.7 | Change **Type** filter to "private" | Settings | Repo list refreshes with private repos only. |
| 30.8 | Click **Clone** on a repo card | Settings → chat | Switches to Neural Link (Chat view). Input pre-filled: `"clone owner/repo from github"`. |
| 30.9 | Click **Issues** on a repo card | Settings → chat | Input pre-filled: `"list issues for owner/repo"`. |
| 30.10 | Click **PRs** on a repo card | Settings → chat | Input pre-filled: `"list pull requests for owner/repo"`. |

### 30-C: GitHub Tools via Chat

| # | Chat Input | Expected Tool | Expected Result |
|---|-----------|--------------|----------------|
| 30.11 | `"list my github repos"` | `github.list_repos` | Formatted list of accessible repos with stars, forks, language, visibility. |
| 30.12 | `"show github issues for owner/repo"` | `github.list_issues` | Open issues: number, title, labels, author, date. |
| 30.13 | `"list pull requests for owner/repo"` | `github.list_prs` | PR list with number, title, author, draft flag, updated date. |
| 30.14 | `"github branches for owner/repo"` | `github.list_branches` | Branch list with protected flag and latest commit SHA. |
| 30.15 | `"show repo info owner/repo"` | `github.repo_info` | Detailed metadata: description, language, stars, forks, default branch, open issues, topics. |
| 30.16 | `"clone owner/repo from github"` | `github.clone` (approval) | Plan step appears with `requires_approval: true` (MEDIUM risk). Authenticated HTTPS clone URL used. |
| 30.17 | `"create github issue in owner/repo titled Bug: crash on start"` | `github.create_issue` | Approval gate → on approve: creates issue, returns `{"number": N, "url": "..."}`. |

### 30-D: REST API direct

```bash
# Connection
curl http://127.0.0.1:8100/github/status
curl -X POST http://127.0.0.1:8100/github/config \
  -H "Content-Type: application/json" -d '{"token": "ghp_abc123"}'
curl http://127.0.0.1:8100/github/test

# Explorer endpoints
curl "http://127.0.0.1:8100/github/repos?limit=10&type=owner&sort=pushed"
curl http://127.0.0.1:8100/github/repos/owner/repo
curl "http://127.0.0.1:8100/github/repos/owner/repo/issues?state=open&limit=20"
curl "http://127.0.0.1:8100/github/repos/owner/repo/pulls?state=open&limit=20"
curl "http://127.0.0.1:8100/github/repos/owner/repo/branches?limit=50"
```

### 30-E: Disconnect & isolation

| # | Action | Expected |
|---|--------|----------|
| 30.18 | Click **Disconnect** in GitHub Connection panel | Token cleared. Status dot turns grey. GitHub Explorer section hidden. Chat commands return "GitHub token not configured". |
| 30.19 | Re-enter PAT and reconnect | Explorer reappears. All tools functional again. |

**Pass criteria:** PAT connects independently of LLM. Explorer renders repo cards. All 7 `github.*` tools reachable via chat + APIs. Clone/create_issue trigger approval gate. Status bar GitHub dot reflects live state. Disconnect isolates GitHub from LLM config.

---

## Scoring

| Act | Capability | Weight |
|-----|-----------|--------|
| 1 | Boot, Health, Home Dashboard | Required |
| 2 | Filesystem (deterministic) | Required |
| 3 | Shell + Policy + Safety | Required |
| 4 | Conversation (LLM) | Optional if no LLM |
| 5 | Command Palette & Keyboard | Nice-to-have |
| 6 | Explorer & Processes | Required |
| 7 | Memory, Workspace, Personality | Required |
| 8 | Error Handling & Recovery | Required |
| 9 | Git Integration (13 tools) | Required |
| 10 | Workflow DSL (24 templates) | Required |
| 11 | Multi-Agent (6 builtins + 21 templates) | Required |
| 12 | Health & Performance | Nice-to-have |
| 13 | Consensus & Negotiation | Nice-to-have |
| 14 | Chains & Pipeline Wizard (35 templates) | Required |
| 15 | **Workflow Studio (visual editor)** | **Required** |
| 16 | Agent Communication | Nice-to-have |
| 17 | Communications & Pipeline Lanes | Nice-to-have |
| 18 | **Security Foundation** | **Required** |
| 19 | **MCP Protocol (Client + Provider)** | **Required** |
| 20 | **LLM Providers (7)** | **Required** |
| 21 | Metrics & Observability | Required |
| 22 | WebSocket Events | Required |
| 23 | RAG & Semantic Search | Optional if no chromadb |
| 24 | Demo Mode (3 tiers) | Nice-to-have |
| 25 | Desktop Shell (Tauri) | Nice-to-have |
| 26 | Background & LLM Config | Nice-to-have |
| 27 | Stress Test | Required |
| 28 | **Context Directory** | **Required** |
| 29 | **Neural Link Enhancements** | **Required** |
| 30 | **GitHub Integration (7 tools + Explorer)** | Required |

**MVP Pass = All "Required" acts pass with no crashes.**

---

## Quick Automated Smoke Test

```powershell
# Health
$h = Invoke-RestMethod http://127.0.0.1:8100/health
Write-Host "OK: version=$($h.version)"

# Tools registered
$tools = Invoke-RestMethod http://127.0.0.1:8100/tools
Write-Host "OK: $($tools.Count) tools"

# Run filesystem command
$r = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8100/run `
  -ContentType "application/json" -Body '{"input":"list ."}'
Write-Host "OK: list $($r.status)"

# Git status
$r = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8100/run `
  -ContentType "application/json" -Body '{"input":"git status"}'
Write-Host "OK: git $($r.status)"

# System status
$sys = Invoke-RestMethod http://127.0.0.1:8100/system/status
Write-Host "OK: system=$($sys.system.hostname)"

# Agent summary
$ag = Invoke-RestMethod http://127.0.0.1:8100/agents/summary
Write-Host "OK: $($ag.total) agents, $($ag.online) online"

# Chain templates (expect 35)
$ct = Invoke-RestMethod http://127.0.0.1:8100/workflow-chain-templates
Write-Host "OK: $($ct.Count) chain templates"

# Agent templates (expect 21)
$at = Invoke-RestMethod http://127.0.0.1:8100/agent-templates
Write-Host "OK: $($at.Count) agent templates"

# Workflow DSL templates (expect 24)
$wt = Invoke-RestMethod http://127.0.0.1:8100/workflow-templates
Write-Host "OK: $($wt.Count) workflow templates"

# Context directory
$ctx = Invoke-RestMethod http://127.0.0.1:8100/context/dir
Write-Host "OK: context_dir=$($ctx.path)"

# GitHub status
$gh = Invoke-RestMethod http://127.0.0.1:8100/github/status
Write-Host "OK: github_connected=$($gh.connected)"

# Security - audit log
$audit = Invoke-RestMethod http://127.0.0.1:8100/security/audit/summary
Write-Host "OK: audit entries=$($audit.total_entries)"

# Security - scrub
$scrub = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8100/security/scrub `
  -ContentType "application/json" -Body '{"text":"key=sk-proj-abc123"}'
Write-Host "OK: scrubbed=$($scrub.scrubbed)"

# MCP servers (expect 5 default)
$mcp = Invoke-RestMethod http://127.0.0.1:8100/mcp/servers
Write-Host "OK: MCP servers=$($mcp.Count)"

# MCP tools (from auto-connected servers)
$mcpTools = Invoke-RestMethod http://127.0.0.1:8100/mcp/tools
Write-Host "OK: MCP tools=$($mcpTools.Count)"

# MCP provider status
$mcpServe = Invoke-RestMethod http://127.0.0.1:8100/mcp/serve/status
Write-Host "OK: MCP provider sessions=$($mcpServe.sessions), tools=$($mcpServe.tools)"

# LLM providers
$llmP = Invoke-RestMethod http://127.0.0.1:8100/llm/providers
Write-Host "OK: LLM providers=$($llmP.Count)"

# LLM status
$llm = Invoke-RestMethod http://127.0.0.1:8100/llm/status
Write-Host "OK: LLM provider=$($llm.provider), available=$($llm.available)"

# Metrics
$md = Invoke-RestMethod http://127.0.0.1:8100/metrics/dashboard
Write-Host "OK: success_rate=$($md.plan_summary.success_rate)"

# Demo mode
$dm = Invoke-RestMethod http://127.0.0.1:8100/demo/status
Write-Host "OK: mode=$($dm.mode)"

Write-Host "`n=== All smoke tests passed ==="
```

---

## Changelog from V5

| Area | V5 (Sprint 60) | V6 (Sprint 62) |
|------|----------------|-----------------|
| Tests | 2193 | 2273 |
| Build Items | 569 | 581 |
| Sprints | 60 | 62 |
| API Endpoints | 224 | 227 (+3 MCP SSE serve endpoints) |
| MCP Protocol | Client only (stdio + SSE) | **Dual-role: Client + Server/Provider** (SSE transport for external clients) |
| MCP Default Servers | — | 5 pre-configured: sequential-thinking, memory, fetch (auto-connect), github, sqlite (disabled) |
| MCP Provider Tools | — | All 52 base tools + 4 virtual tools (machina.create_task, machina.get_task, machina.list_tasks, machina.chat) |
| MCP Provider Resources | — | 17 resources across 7 domains (workspace, memory, events, security, agents, tasks, telemetry) |
| MCP Provider Prompts | — | 4 templates (plan_task, analyze_code, scrub_credentials, explain_error) |
| MCP SSE Endpoints | — | GET /mcp/serve/sse, POST /mcp/serve/messages, GET /mcp/serve/status |
| MCP UI Sub-Tabs | 2 (Servers, Tools) | 4 (Servers, Tools, Resources, Prompts) |
| MCP Agent | — | agent_mcp builtin (capabilities: mcp, mcp_tool; tool_filter: mcp.*) |
| Builtin Agents | 5 | 6 (+ mcp agent) |
| Act 19 Weight | Nice-to-have | **Required** (expanded from 6 to 30 steps covering client + provider) |
| Scoring | MCP Nice-to-have | MCP **Required** |
