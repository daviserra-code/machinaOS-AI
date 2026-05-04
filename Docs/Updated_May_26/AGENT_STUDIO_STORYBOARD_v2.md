# Machina OS — Agent, Studio & MCP Storyboard

> **UI-driven step-by-step walkthroughs** demonstrating multi-agent coordination, Workflow Studio, and MCP integration.
> Every act is performed through the Machina OS web UI at `http://127.0.0.1:8100`.
> Acts are ordered from basic to complex. Each builds on the previous.

---

## Prerequisites

1. **Server running** — `python -m uvicorn apps.api.server:app --host 127.0.0.1 --port 8100 --reload`
2. **Open the UI** — navigate to `http://127.0.0.1:8100` in your browser
3. **(Optional)** Ollama running for LLM-powered features — `ollama serve`
4. **(Optional)** Node.js installed for MCP servers (Part IV)

---

## Part I — Agent Fleet Operations

### Act 1: Fleet Health Dashboard

**Goal:** Get a bird's-eye view of the entire agent fleet — who's online, their health, and capabilities.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 1.1 | Click **Agents** in the nav bar (or press `Ctrl+7`) | Nav bar | Agents view opens on the **Fleet** sub-tab. |
| 1.2 | Check the **Agent Fleet Status Bar** at the bottom of the page | Status bar | Shows online/degraded/offline dot counts (e.g. "6 online · 0 degraded · 0 offline") and top performer name. |
| 1.3 | Review the **agent cards** in the Fleet panel | Fleet tab | Each builtin agent listed: filesystem, git, shell, system, browser, vscode. Cards show name, description, tool_filter globs, capabilities. |
| 1.4 | Click the **Performance** sub-tab | Agent sub-tabs | Performance Dashboard loads with agent comparison cards showing reputation score, success rate, and average latency for each agent. |
| 1.5 | Click the **Monitoring** sub-tab | Agent sub-tabs | Health panel shows each agent with status indicator (green dot = ONLINE), total checks, average latency, and error streak count. |
| 1.6 | Select an agent from the **Health History** dropdown | Monitoring tab | Check log appears showing success/failure dots per health check with latency values and timestamps. |
| 1.7 | Select an agent from the **Performance Trends** dropdown | Monitoring tab | SVG time-series chart renders with two lines: amber = reputation score, green = success rate. Summary cards show Score, Success%, and Latency. |
| 1.8 | Click the **Capability Discovery** section, select an agent | Monitoring tab | Table shows all discovered tools for that agent with source (filter/history) badges and confidence scores. |

**Pass criteria:** All 6+ builtin agents visible and ONLINE. Performance and health panels render with data (metrics may be zeroes on a fresh system — that's normal).

---

### Act 2: Spin Up a Specialist Agent from Template

**Goal:** Create a security auditor agent from a blueprint template and verify it joins the fleet.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 2.1 | In the **Fleet** sub-tab, click the **"From Template"** button | Fleet tab | A glassmorphic template picker modal opens listing all available agent blueprints (21+). Each shows name, description, capability badges, and tool_filter badges. |
| 2.2 | Find **"security-auditor"** in the template list and click it | Template picker | Modal closes. A new agent card appears in the fleet list: "Security Auditor" with security-related capabilities (grep, search, read_file) and tool_filter globs. |
| 2.3 | Check the **status bar** at the bottom | Status bar | Fleet count increased by 1 (e.g. "7 online"). |
| 2.4 | Switch to the **Monitoring** sub-tab | Agent sub-tabs | The new security-auditor agent appears in the health list with ONLINE status. |
| 2.5 | Select the new agent in the **Capability Discovery** dropdown | Monitoring tab | Discovered capabilities table shows all tools matching its `filesystem.grep`, `filesystem.search`, `filesystem.read_file` filter globs with source = "filter". |
| 2.6 | Switch back to **Fleet**, click the **edit** (pencil) icon on the new agent card | Fleet tab | Agent editor opens with pre-filled fields: name, description, capabilities, tool_filter, system_prompt. All editable. |
| 2.7 | Click **Save** without changes (or tweak the description first) | Agent editor | Agent saved. Toast notification confirms. |

**Pass criteria:** Agent created from template with correct capabilities. Fleet count increases. Agent is ONLINE in health monitoring.

---

### Act 2b: Deep Dive — Crafting the Perfect System Prompt

**Goal:** Open the Security Auditor's editor, understand how the system prompt influences LLM behaviour during planning and delegation, and write a production-grade prompt using the built-in writing guide.

> **Background:** Every agent has a `system_prompt` field. When the planner LLM builds an execution plan, the prompt is injected into the agent catalog so the LLM understands *how* each agent should behave — not just what tools it owns. A well-written prompt makes an agent predictable, safe, and task-focused.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 2b.1 | In the **Fleet** tab, click the **edit** (pencil) icon on the **Security Auditor** card | Fleet tab | Agent editor opens. The **System Prompt** textarea shows the template default: *"You are a security auditor. Scan codebases for leaked secrets, insecure patterns, missing access controls, and compliance gaps."* |
| 2b.2 | Note the **character counter** in the top-right corner of the textarea | Agent editor | Shows the current prompt length (e.g. "104 chars"). Updates live as you type. |
| 2b.3 | Click the **▸ Prompt Writing Guide** disclosure below the textarea | Agent editor | An inline guide expands with two columns: **✓ Do** (role declaration, core responsibilities, safety constraints, output format, escalation rules) and **✗ Avoid** (vague instructions, contradicting tool filters, overly long prompts, secrets in the prompt, overriding safety policies). |
| 2b.4 | Read the **example prompt** at the bottom of the guide panel | Agent editor | Shows a mono-spaced sample: *"You are a security auditor. Scan codebases for leaked secrets, insecure patterns, missing access controls, and compliance gaps. Flag findings by severity (critical / high / medium / low). Prefer safe read-only operations. Never modify source files."* |
| 2b.5 | Clear the textarea and type a new prompt following the guide's structure: | Agent editor | Textarea accepts the new prompt. Character counter updates in real-time. |
|     | **Role:** `You are a security-focused code auditor.` | | |
|     | **Responsibilities:** `Scan for hardcoded secrets (API keys, tokens, passwords), insecure code patterns (eval, exec, os.system), missing .gitignore rules, and dependency vulnerabilities.` | | |
|     | **Output format:** `Flag each finding with a severity level: critical, high, medium, or low. Group results by file.` | | |
|     | **Safety:** `Prefer safe read-only operations. Never modify, delete, or write to source files.` | | |
|     | **Escalation:** `If a critical finding is detected, recommend immediate human review before proceeding.` | | |
| 2b.6 | Verify the complete prompt reads roughly: *"You are a security-focused code auditor. Scan for hardcoded secrets (API keys, tokens, passwords), insecure code patterns (eval, exec, os.system), missing .gitignore rules, and dependency vulnerabilities. Flag each finding with a severity level: critical, high, medium, or low. Group results by file. Prefer safe read-only operations. Never modify, delete, or write to source files. If a critical finding is detected, recommend immediate human review before proceeding."* | Agent editor | ~280 chars — well under the recommended 300 char soft limit. |
| 2b.7 | Click **Save Agent** | Agent editor | Toast notification: "Agent saved". Editor closes. |
| 2b.8 | Switch to **Chat** (`Ctrl+2`). Type `delegate to security-auditor scan this project for leaked secrets` and press Enter | Neural Link | Plan card appears. The planner sees the agent's system prompt and routes to the security auditor with `filesystem.grep` tool. The plan description reflects the security focus — e.g. searching for `api_key\|secret\|password\|token`. |
| 2b.9 | Check the plan step's `delegate_to` field | Plan card | Shows `delegate_to: agent_<security-auditor-id>` confirming the prompt guided the planner to choose this specialist agent. |
| 2b.10 | Return to **Agents** → **Fleet**, edit the Security Auditor again. Note how the saved prompt persists across sessions (stored in SQLite) | Agent editor | The prompt you typed in 2b.5 is still there, exactly as saved. |

**Key takeaways for presenters:**

- **Role + Responsibilities + Output Format + Safety + Escalation** = the 5-part prompt formula
- The system prompt is injected into the planner LLM's agent catalog — it directly influences which agent gets delegated to and how the plan is structured
- Templates ship with minimal 1–2 sentence prompts; production deployments should expand them using the guide
- The prompt is persisted to SQLite and survives server restarts
- Built-in agents (filesystem, git, shell, system, browser, vscode) also ship with safety-oriented prompts

**Pass criteria:** Prompt writing guide expands with actionable Do/Avoid columns. New prompt saves and persists. Delegation in Chat respects the agent's system prompt context.

---

### Act 3: Agent-to-Agent Delegation via Chat

**Goal:** Use the Neural Link (chat) to delegate tasks to specific agents and observe the delegation flow.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 3.1 | Click **Chat** (or press `Ctrl+2`) | Nav bar | Chat view opens with the Neural Link input at the bottom. |
| 3.2 | Type `delegate to filesystem list files in current directory` and press Enter | Neural Link | Plan card appears with `filesystem.list` tool, `delegate_to: agent_filesystem`. Step executes and shows directory listing with 📁/📄 icons. |
| 3.3 | Type `delegate to git show repository status` and press Enter | Neural Link | Plan card with `git.status`, `delegate_to: agent_git`. Shows branch name, clean/dirty status, file counts. |
| 3.4 | Type `ask agent system check memory` and press Enter | Neural Link | Plan card with `system.memory`, `delegate_to: agent_system`. Shows Available/Used GB in formatted cards. |
| 3.5 | Switch to **Agents** → **Fleet** sub-tab | Nav bar | Agent fleet view. |
| 3.6 | Scroll down to the **Agent Message Log** section | Fleet tab | Messages appear showing delegation events: source_agent → target_agent with message_type = "delegation_request". |
| 3.7 | Click the **Threads** toggle button above the message log | Fleet tab | Messages group by correlation_id into collapsible thread cards. Each thread shows participant list and message count badge. |

**Pass criteria:** Each delegation routes to the correct agent and tool. Agent message log records the delegation events. Thread view groups related messages.

---

### Act 4: Multi-Agent Consensus Voting

**Goal:** Create a consensus request, have multiple agents vote, and resolve the outcome.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 4.1 | Go to **Agents** → **Coordination** sub-tab | Agent sub-tabs | Coordination panels load: Consensus, Negotiations, Handoffs, Broadcasts, Collaborations, Agent Requests. |
| 4.2 | In the **Consensus** panel, fill in the create form: Question = `Is it safe to push to production?`, Candidates = `agent_filesystem, agent_git, agent_system`, Strategy = `MAJORITY`, Min Voters = `2` | Coordination tab | Form fields accept input. |
| 4.3 | Click **Create Consensus** | Consensus panel | New consensus card appears with status = PENDING, showing the question, candidates, and strategy. |
| 4.4 | On the consensus card, click the **Vote** button for `agent_filesystem` → select **APPROVE**, enter reason `No uncommitted changes detected`, click submit | Consensus card | Vote recorded. Card updates to show 1 vote cast. |
| 4.5 | Click **Vote** for `agent_git` → **APPROVE** with reason `Branch is up to date with remote` | Consensus card | 2 votes cast. |
| 4.6 | Click **Vote** for `agent_system` → **REJECT** with reason `Disk usage above 85%`, weight = `0.5` | Consensus card | 3 votes cast. |
| 4.7 | Click the **Resolve** button on the consensus card | Consensus card | Status changes to RESOLVED (2 approvals vs 1 rejection → MAJORITY passes). Card shows green "RESOLVED" badge. |
| 4.8 | Scroll down to the **Consensus Patterns** section | Coordination tab | Table shows the pattern with 1 approval recorded, approval rate, and auto-skip indicator (not yet — needs ≥10 samples with >95% rate). |

**Pass criteria:** Consensus flows through PENDING → voting → RESOLVED. Majority vote (2 APPROVE > 1 REJECT) resolves correctly. Pattern learning records the outcome.

---

### Act 5: Agent Negotiation — Who Handles the Task?

**Goal:** Two agents negotiate over who should handle a specific tool. Observe the full negotiation lifecycle.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 5.1 | In the **Coordination** sub-tab, scroll to the **Negotiations** panel | Coordination tab | Negotiation create form and existing negotiations list. |
| 5.2 | Fill the form: Initiator = `agent_filesystem`, Responder = `agent_git`, Tool = `filesystem.grep`, Priority = `NORMAL`, Reason = `I have direct grep capabilities in my tool filter` | Negotiations panel | Form fields populated. |
| 5.3 | Click **Create Negotiation** | Negotiations panel | New negotiation card appears with phase = PROPOSED (cyan badge). Shows initiator, responder, tool, and priority. |
| 5.4 | Click the **Counter** button on the card → enter reason `I can search through git history for more context`, click submit | Negotiation card | Phase changes to COUNTERED (amber badge). Round number increments. |
| 5.5 | Click the **Auto-Counter** button | Negotiation card | System suggests the best alternative agent based on capability confidence. Shows counter_agent and confidence score. |
| 5.6 | Click the **Auto-Resolve** button | Negotiation card | Phase changes to RESOLVED (purple badge). Winner is determined by priority rules. Card shows the winner agent. |
| 5.7 | Switch to **Communications** sub-tab | Agent sub-tabs | Activity feed shows negotiation events: negotiation_proposed → negotiation_countered → negotiation_resolved with timestamps. |
| 5.8 | In the **Negotiation Timeline** section, paste the negotiation ID | Communications tab | Vertical timeline renders with phase-colored dots: cyan (proposed) → amber (countered) → purple (resolved). Each entry shows round number, agent, and reason. |

**Pass criteria:** Negotiation flows through PROPOSED → COUNTERED → RESOLVED. Timeline shows complete round-by-round history. Communications feed records all events.

---

### Act 6: Task Handoff Between Agents

**Goal:** One agent requests a handoff to another, which accepts and completes the work.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 6.1 | In the **Coordination** sub-tab, scroll to the **Handoffs** panel | Coordination tab | Handoff create form and list. |
| 6.2 | Fill the form: From = `agent_shell`, To = `agent_filesystem`, Tool = `filesystem.delete`, Reason = `Need temp files cleaned before deployment` | Handoffs panel | Form populated. |
| 6.3 | Click **Create Handoff** | Handoffs panel | New handoff card appears with status = REQUESTED. Shows from → to agents, tool, and reason. |
| 6.4 | Click the **Accept** button on the card | Handoff card | Status changes to ACCEPTED (green badge). |
| 6.5 | Click the **Complete** button | Handoff card | Status changes to COMPLETED. Resolved timestamp appears. Full lifecycle visible: created_at → resolved_at. |
| 6.6 | Check the **Communications** sub-tab → activity feed | Communications tab | Events show: handoff_requested → handoff_accepted → handoff_completed with purple edge colors in the communication graph. |

**Pass criteria:** Handoff progresses REQUESTED → ACCEPTED → COMPLETED. Timestamps track the full lifecycle.

---

### Act 7: Broadcast Intelligence Gathering

**Goal:** Broadcast a question to all agents, collect responses, and aggregate results.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 7.1 | In the **Coordination** sub-tab, scroll to the **Broadcast Queries** panel | Coordination tab | Broadcast create form. |
| 7.2 | Fill: From Agent = `orchestrator`, Question = `Report any concerns about the current workspace state`, Target Agents = `agent_filesystem, agent_git, agent_system` | Broadcast panel | Form populated. |
| 7.3 | Click **Create Broadcast** | Broadcast panel | New query card appears with status = PENDING/COLLECTING. Shows question and target agents. |
| 7.4 | Click **Respond** on the card for `agent_filesystem` → enter payload (e.g. `{"concern": "Found 3 .tmp files", "severity": "low"}`) | Broadcast card | Response recorded. Card updates with response count. |
| 7.5 | Repeat for `agent_git` (payload: `{"concern": "2 uncommitted files", "severity": "medium"}`) and `agent_system` (payload: `{"concern": "Disk at 72%", "severity": "none"}`) | Broadcast card | 3 responses collected. |
| 7.6 | Click the **Complete** button | Broadcast card | Status changes to COMPLETED. |
| 7.7 | Click the **Aggregate** button → select strategy **MERGE** | Broadcast card | Aggregated result appears inline showing all agent payloads merged into one combined view. Response count displayed. |
| 7.8 | Try creating a second broadcast, set the **Timeout** field to `30000` (30s) | Broadcast panel | Timeout badge appears on the query card. After 30 seconds, the query auto-expires if not completed. |

**Pass criteria:** Broadcast collects responses from multiple agents. MERGE aggregation combines payloads. Timeout badge displays and auto-expiry works.

---

### Act 8: Agent Collaboration Session

**Goal:** Create a shared collaboration session where multiple agents contribute context for a debugging task.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 8.1 | In the **Coordination** sub-tab, scroll to **Collaboration Sessions** | Coordination tab | Collaboration create form. |
| 8.2 | Fill: Task ID = `debug_memory_leak_2024`, Participants = `agent_filesystem, agent_git, agent_system` | Collaboration panel | Form populated. |
| 8.3 | Click **Create Collaboration** | Collaboration panel | New session card appears showing session_id, task_id, 3 participants listed, and context key count = 0. |
| 8.4 | Click on the session card to expand it. Add context: Key = `memory_baseline`, Value = `RSS 450MB at startup, growing 2MB/hour` | Session detail | Context added. Key count updates to 1. |
| 8.5 | Add more context entries: `recent_commits` = `Last 3 commits touched core/events/`, `large_files` = `events.db grew from 12MB to 89MB in 24 hours` | Session detail | Key count = 3. All context entries visible. |
| 8.6 | Click **Join** and add `agent_shell` as a new participant | Session detail | Participant list grows to 4 agents. |
| 8.7 | Click **Close** to end the collaboration | Session detail | Session marked closed. Closed timestamp appears. is_active = false. |

**Pass criteria:** Collaboration tracks participants and shared context. Agents can join mid-session. Context accumulates and is visible to all.

---

### Act 9: Smart Task Queue & Auto-Execution

**Goal:** Enqueue tasks for different agents at various priorities, then auto-execute them in priority order.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 9.1 | Go to **Agents** → **Pipelines** sub-tab, scroll to **Agent Task Queue** | Pipelines tab | Task queue form and list. |
| 9.2 | Enqueue a high-priority task: Agent = `agent_system`, Tool = `system.memory`, Priority = `1` → click **Enqueue** | Pipelines tab | Task card appears with status = QUEUED, priority badge = 1. |
| 9.3 | Enqueue: Agent = `agent_system`, Tool = `system.disk`, Priority = `2` → Enqueue | Task Queue | Second task added. Queue sorted by priority (1 first, then 2). |
| 9.4 | Enqueue: Agent = `agent_filesystem`, Tool = `filesystem.list`, Priority = `3` → Enqueue | Task Queue | Third task. |
| 9.5 | Enqueue: Agent = `agent_git`, Tool = `git.status`, Priority = `1` → Enqueue | Task Queue | Fourth task. Now two priority-1 tasks visible at top. |
| 9.6 | Click the **⚡ Auto-Execute** button on the first QUEUED task (system.memory, priority 1) | Task card | Task executes. Status changes to COMPLETED. Real memory data appears in the result. |
| 9.7 | Click the **Auto-Execute All** button for `agent_system` | Task Queue | All remaining system agent tasks drain in priority order. Both show COMPLETED with real results (memory and disk data). |
| 9.8 | Click **⚡ Auto-Execute** on the filesystem.list and git.status tasks | Task cards | Both execute with real results: directory listing and git status output. |
| 9.9 | Review the queue — all tasks should show COMPLETED status | Task Queue | Green COMPLETED badges on every task. |

**Pass criteria:** Tasks enqueue with correct priorities. Auto-execute runs them and returns real tool results. Priority order is respected.

---

### Act 10: Agent Communication Graph

**Goal:** After completing the previous acts, review the communication patterns between agents.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 10.1 | Click the **Communications** sub-tab | Agent sub-tabs | Communications dashboard loads with stats cards, SVG graph, and activity feed. |
| 10.2 | Check the **stats cards** at the top | Communications tab | Cards show: total messages, negotiations count, pending requests, active collaborations. Values reflect the acts you performed. |
| 10.3 | Examine the **SVG communication graph** | Communications tab | Circular layout with agent nodes. Color-coded directed edges: cyan = requests, amber = negotiations, purple = handoffs, emerald = broadcasts. Edge labels show message counts. |
| 10.4 | Scroll down to the **Activity Feed** | Communications tab | Unified timeline of all inter-agent events (consensus votes, negotiations, handoffs, broadcasts, collaborations) with Material icons and status badges. Newest first. |
| 10.5 | Use the **type filter dropdown** above the feed | Activity feed | Filter to show only specific event types (e.g. just negotiations, or just handoffs). |
| 10.6 | Check the **Message Threading** section — click the **Threads** toggle | Communications tab | Messages grouped by correlation_id into collapsible thread cards with participant lists and message counts. |

**Pass criteria:** Communication graph shows agent relationships from all previous acts. Activity feed reflects all inter-agent events. Thread view groups related conversations.

---

## Part II — Workflow Chains: Real-World Pipelines

### Act 11: Pre-Commit Health Check from Template

**Goal:** Create a workflow chain from a built-in template, execute it, and review the results.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 11.1 | Go to **Agents** → **Pipelines** sub-tab | Agent sub-tabs | Pipeline panels load: Chain Execution History, Agent Task Queue, Workflow Chains, Pipeline Lane View. |
| 11.2 | Scroll down to the **Workflow Chains** section and click the **"Use Template"** button | Workflow Chains section | Template picker opens below the button showing 35 chain templates with names, descriptions, step counts, and a search filter. |
| 11.3 | Type **"pr"** in the search box, then click **Use** on **"pr-readiness-check"** | Template picker | Picker closes. New chain appears in the Workflow Chains list: "PR Readiness Check" with 5 steps. Card shows step flow: git.status → git.diff → filesystem.search (test files) → filesystem.grep (TODO markers) → git.log. |
| 11.4 | Click the **Execute** button on the chain card | Chain card | Execution starts. After completion, a result summary appears: succeeded/failed/skipped step counts with ✓/✗/⊘ badges per step. |
| 11.5 | Expand the execution results to inspect each step's output | Chain card | Each step shows the real tool output: diff content, TODO matches, commit history, branch status. |
| 11.6 | Click the **Execute** button again to run a second time | Chain card | Second execution recorded. |
| 11.7 | Scroll down to the **Chain Execution History** section | Pipelines tab | History shows 2 execution records for this chain with status (SUCCESS/PARTIAL/FAILED), timestamps, and step counts (✓✗⊘). |

**Pass criteria:** Template creates a multi-step pipeline. Execution returns real tool results. History records multiple runs.

---

### Act 12: Custom Security Audit Pipeline

**Goal:** Build a custom 6-step security audit chain with data flow, optimize it for parallelism, and execute.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 12.1 | In the **Pipelines** sub-tab, scroll to **Workflow Chains** and click **+ New Chain** | Workflow Chains section | Chain creation form opens with name, description, and step editor. |
| 12.2 | Enter Name = `Security Audit Pipeline`, Description = `Comprehensive security scan with parallel analysis` | Form | Fields populated. |
| 12.3 | Add **Step 1**: Agent = `Filesystem Agent`, Tool = `filesystem.grep`, Description = `Scan for hardcoded secrets`, Output Key = `secrets_scan`. In the argument fields, set Search Pattern = `api_key\|secret\|password\|token`, Search In = `.` | Step editor | Step 1 configured — selecting `filesystem.grep` shows labeled fields (Search Pattern, Search In) instead of raw JSON. |
| 12.4 | Click **+ Add Step**. Add **Step 2**: Agent = `Filesystem Agent`, Tool = `filesystem.read_file`, Description = `Check .gitignore`, Output Key = `gitignore_check`. Set File Path = `.gitignore` | Step editor | Step 2 added below Step 1. |
| 12.5 | Add **Step 3**: Agent = `Filesystem Agent`, Tool = `filesystem.grep`, Description = `Dangerous code patterns`, Output Key = `dangerous_patterns`. Set Search Pattern = `eval(\|exec(\|os.system`, Search In = `.` | Step editor | Step 3 added. |
| 12.6 | Add **Step 4**: Agent = `Filesystem Agent`, Tool = `filesystem.search`, Description = `Find env files`, Output Key = `env_files`. Set File Pattern = `*.env*`, Search In = `.` | Step editor | Step 4 added. |
| 12.7 | Add **Step 5**: Agent = `Git Agent`, Tool = `git.status`, Description = `Untracked sensitive files`, Output Key = `git_state`. Set Repository Path = `.` | Step editor | Step 5 — note the agent changes to Git Agent. |
| 12.8 | Add **Step 6**: Agent = `System Agent`, Tool = `system.info`, Description = `System audit trail`, Output Key = `system_context`. No argument fields shown (system.info takes no parameters) | Step editor | Step 6 — agent is System Agent, no arguments needed. |
| 12.9 | Click **Create Chain** | Form | Chain created. New card appears in the chains list with 6 steps across 3 agents. Vertical flow visualization shows colored badges: emerald (output_key), agent indicators. |
| 12.10 | Click the **Optimize** button on the chain card | Chain card | Toast notification shows "Optimized: X parallel groups found". Steps that have no data dependencies are grouped for concurrent execution. |
| 12.11 | Click the **∥ Parallel** execute button | Chain card | Parallel execution runs grouped steps concurrently. Results show all 6 steps with real data: grep matches, .gitignore contents, search results, git status, system info. |
| 12.12 | Click the **Auto-Assign** button | Chain card | System reassigns agents based on capability confidence. Toast confirms agents updated. |

**Pass criteria:** 6-step chain creates across 3 agents. Optimization identifies parallel groups. Parallel execution runs grouped steps concurrently. All steps return real workspace data.

---

### Act 13: Conditional Pipeline with Cross-Agent Branching

**Goal:** Build a pipeline with conditions and branch logic, then execute and observe step gating.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 13.1 | Create a new chain: Name = `Deploy Readiness`, Description = `Conditional checks with branching` | Pipelines tab | Form ready. |
| 13.2 | Add **Step 1**: Agent = `agent_git`, Tool = `git.status`, Output Key = `git_state`. Args: cwd = `.` | Step editor | Step 1 configured. |
| 13.3 | Add **Step 2**: Agent = `agent_filesystem`, Tool = `filesystem.list`, Output Key = `project_files`. Args: path = `.`. Expand **Advanced Options** → set Condition = `git_state:branch not_empty` | Step editor | Condition field shows in the advanced section. This step only runs if git_state has a branch value. |
| 13.4 | Add **Step 3**: Agent = `agent_filesystem`, Tool = `filesystem.tree`, Output Key = `project_tree`. Set Input From = `project_files`. Args: path = `.`, max_depth = `2` | Step editor | Input From links this step's input to Step 2's output. |
| 13.5 | Add **Step 4**: Agent = `agent_system`, Tool = `system.memory`, Output Key = `memory_check`. Set Parallel Group = `resource_checks` | Step editor | Parallel group field visible in advanced options. |
| 13.6 | Add **Step 5**: Agent = `agent_system`, Tool = `system.disk`, Output Key = `disk_check`. Set Parallel Group = `resource_checks`. Args: path = `.` | Step editor | Same parallel group → these two steps run concurrently. |
| 13.7 | Click **Create** | Form | Chain card shows 5 steps with colored badges: amber ⚡ (condition), sky (input_from), teal ∥ (parallel_group). |
| 13.8 | Click **Execute** | Chain card | Execution runs. Step 1 (git.status) executes first. Step 2 evaluates its condition (branch not_empty → should pass). Step 3 receives Step 2's output via bridging. Steps 4-5 run in parallel. Results show condition_met status per step. |
| 13.9 | Click the **History** button on the chain card | Chain card | Version history panel shows v1 with creation timestamp. |
| 13.10 | Click **Edit** → modify the description → **Save** | Chain card | Version increments to v2. History now shows both versions. |
| 13.11 | Click **Rollback** → select version 1 | Chain card | Chain reverts to v1 state. Toast confirms rollback. |

**Pass criteria:** Conditions gate step execution. Input_from bridges data between steps. Parallel groups run concurrently. Versioning and rollback work.

---

### Act 14: Pipeline Negotiation & Conflict Resolution

**Goal:** Negotiate which agent handles each step in a chain. Resolve conflicts when agents tie.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 14.1 | Create a chain with ambiguous assignments: Name = `Cross-Team Analysis`. Steps: (1) filesystem.tree, (2) filesystem.grep, (3) git.log, (4) git.diff, (5) system.info — all assigned to their natural agents | Pipelines tab | Chain created with 5 steps. |
| 14.2 | Click the **Negotiate** button on the chain card | Chain card | Negotiation runs. Results appear inline showing: assignments (agent → tool with confidence score) and any conflicts (tied agents for a step). |
| 14.3 | If **conflicts** are detected (e.g. two agents score equally for filesystem.grep), click **Resolve Conflicts** | Conflict picker | Radio buttons appear for each tied step showing the candidate agents. Select your preferred agent for each conflict. |
| 14.4 | Click **Apply Resolution** | Conflict picker | Conflicts resolved. Chain updated with selected agents. Version increments. |
| 14.5 | Switch to the **Pipeline Lane View** section | Pipelines tab | Horizontal lanes appear, one per agent. Steps are positioned in their assigned agent's lane as draggable badges. |
| 14.6 | **Drag** a step badge from one agent lane to another | Lane view | Step moves to the new agent's lane with visual ring feedback. Chain auto-saves (version increments). |
| 14.7 | Click the **Negotiate All** button | Pipeline lane view | Bulk negotiation runs across ALL workflow chains. Toast shows total assignments and conflicts found. |

**Pass criteria:** Negotiation scores agents by confidence. Conflicts detected and resolvable via picker. Lane view allows drag-and-drop agent reassignment. Negotiate All processes all chains.

---

### Act 15: Chain Execution Replay

**Goal:** Replay a previous chain execution with modified arguments.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 15.1 | Go to the **Chain Execution History** section in Pipelines | Pipelines tab | List of previous executions with status colors, step counts, and timestamps. |
| 15.2 | Find a completed execution and click the **Replay** button on its card | Execution card | Replay form opens with the original chain's arguments pre-filled. Override fields let you change specific step arguments. |
| 15.3 | Modify an argument (e.g. change a grep query from `TODO` to `FIXME\|HACK`) | Replay form | Argument override applied. |
| 15.4 | Click **Replay** | Replay form | Chain re-executes with the modified arguments. New execution record created and linked to the original (source_execution_id). |
| 15.5 | Check the execution history — both original and replay should appear | Execution history | Two entries: original and replay, linked by source execution ID. |

**Pass criteria:** Replay creates a new execution from a previous one. Argument overrides apply. Original and replay are linked in history.

---

## Part III — Workflow Studio Visual Editor

### Act 16: Build a Pipeline Visually in Studio

**Goal:** Use the Workflow Studio to visually construct a code review pipeline by dragging tools onto a canvas, connecting them, and executing.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 16.1 | Click **Studio** in the nav bar (or press `Ctrl+6`) | Nav bar | Workflow Studio opens with three panels: left palette, center SVG canvas (grid background), right properties panel. |
| 16.2 | In the left palette, click the **Tools** tab. Type `filesystem` in the filter | Palette | Tool list filters to show only filesystem tools. |
| 16.3 | **Drag** `filesystem.tree` from the palette onto the canvas | Canvas | A node appears on the canvas representing filesystem.tree. |
| 16.4 | **Drag** `filesystem.grep` onto the canvas below the first node | Canvas | Second node appears. |
| 16.5 | **Drag** `git.status` onto the canvas | Canvas | Third node. |
| 16.6 | **Drag** `git.log` onto the canvas | Canvas | Fourth node. Now 4 nodes on canvas. |
| 16.7 | Click on the **filesystem.tree** node to select it | Properties panel | Properties panel populates with fields: Tool (filesystem.tree), Agent dropdown, Output Key, Input From, and the smart argument builder with path and max_depth fields. |
| 16.8 | Set: path = `.`, max_depth = `3`, Output Key = `structure`, Agent = `agent_filesystem` | Properties panel | Node reflects the configuration. Tool description shown below the dropdown for reference. |
| 16.9 | Click the **filesystem.grep** node. Set: path = `.`, query = `TODO\|FIXME`, Output Key = `markers`, Agent = `agent_filesystem` | Properties panel | Second node configured. |
| 16.10 | Click the **git.status** node. Set: cwd = `.`, Output Key = `repo_state`, Agent = `agent_git` | Properties panel | Third node configured. |
| 16.11 | Click the **git.log** node. Set: cwd = `.`, limit = `5`, Output Key = `recent_changes`, Agent = `agent_git` | Properties panel | Fourth node configured. |
| 16.12 | **Connect nodes**: Drag from the output port (right side) of the filesystem.tree node to the input port (left side) of the filesystem.grep node | Canvas | A curved Bezier edge appears connecting the two nodes. The grep node's Input From auto-populates with `structure`. |
| 16.13 | Enter a chain name: `Visual Code Review` in the name field at the top | Properties panel | Name set. |
| 16.14 | Click the **Save** button | Toolbar | Chain saved. Toast notification confirms with the chain_id. |
| 16.15 | Click the **Execute** button | Toolbar | Execution runs. Results tray opens at the bottom showing each step's output with real data from your workspace: project tree, TODO/FIXME matches, git status, commit log. |

**Pass criteria:** 4 nodes created via drag-and-drop. Edge connects tree → grep with auto Input From. Execution returns real data. Chain persisted.

---

### Act 17: Studio Debug Execution with Stepping Controls

**Goal:** Run a chain in debug mode using the stepping debugger, controlling execution one step at a time.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 17.1 | In Studio, open an existing chain: click the **Open Chain** button | Toolbar | Glassmorphic picker modal opens showing all saved chains with step counts and agent names. |
| 17.2 | Select a chain from the picker (e.g. "Visual Code Review" from Act 16) | Picker modal | Chain loads into the canvas with auto-positioned nodes and edges. |
| 17.3 | Click the **Debug** button (🐛 icon) | Toolbar | Debug session created on server. Debug toolbar appears with **Step Over**, **Continue**, and **Stop** buttons. Step counter shows "0 / N". All pending steps shown in results tray. |
| 17.4 | Click **Step Over**: Node 1 gets an **amber pulsing border + spinner** while executing | Canvas | First node has animated amber glow and loading spinner overlay. Step/Continue buttons disabled during execution. |
| 17.5 | When Node 1 completes: it gets a **green glow + ✓ badge**. Step counter updates to "1 / N". | Canvas + Toolbar | Visual state transition. Green = success. Results tray shows output with duration (e.g. "filesystem.tree — 120ms"). |
| 17.6 | Click **Step Over** again to execute Node 2 | Canvas | Node 2 transitions: amber (running) → green ✓ (success). Each step controlled individually. |
| 17.7 | Click **Continue** to run all remaining steps | Canvas + Results tray | Remaining nodes execute in sequence with amber→green/red transitions. Results tray auto-scrolls to current step. |
| 17.8 | **Resize the results tray**: drag the handle at the top edge of the tray | Results tray | Tray height adjusts (min 80px, max 80vh). All step outputs visible with duration metrics. |
| 17.9 | After completion, all nodes show their final status badges on the canvas | Canvas | Visual pipeline state: all green ✓ for a successful run, or a mix of ✓/✗/⊘ if some steps failed or were skipped. |

**Pass criteria:** Debug mode creates a server-side session. Stepping toolbar (Step Over/Continue/Stop) controls execution pace. Canvas shows real-time node state changes (amber→green/red). Results stream incrementally in resizable tray. Duration metrics per step.

---

### Act 18: Load a Template into Studio and Customize

**Goal:** Load a chain template into the visual editor, modify it, and save as a custom pipeline.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 18.1 | In Studio, click the **Templates** tab in the left palette | Palette | List of chain templates and workflow DSL templates. |
| 18.2 | Click **"security-deep-scan"** | Palette | Template loads into the canvas with pre-positioned nodes, auto-connected edges, and pre-filled arguments. Canvas auto-fits to show all nodes if the chain has 5+ steps. |
| 18.3 | Click on the grep node → in the smart argument builder, change the `query` field to add project-specific patterns (e.g. `eval\|exec\|hardcoded_secret`) | Properties panel | Argument updated in the form field. |
| 18.4 | Drag `system.disk` from the Tools palette onto the canvas below the last node | Canvas | New node added. |
| 18.5 | Connect the last existing node's output port to the new system.disk node's input port | Canvas | Bezier edge drawn. |
| 18.6 | Configure the new node: Output Key = `disk_audit`, Agent = `agent_system`, path = `.` | Properties panel | Node configured. |
| 18.7 | Change the chain name to `Custom Security Scan v2` | Name field | Name updated. |
| 18.8 | Click **Auto-Assign** | Toolbar | System assigns best agents per node based on capability confidence. Agent dropdowns may update. |
| 18.9 | Click **Optimize** | Toolbar | System identifies parallel groups from the dependency graph. Toast shows group count. |
| 18.10 | Click **Save** | Toolbar | Custom chain persisted. |
| 18.11 | Click **Execute** | Toolbar | Chain runs with real results. |

**Pass criteria:** Template loads with pre-configured nodes and edges. Customization (add node, change args) works. Auto-Assign and Optimize apply. Saved as a new custom chain.

---

### Act 18a: Canvas Zoom & Pan

**Goal:** Navigate a large pipeline using zoom and pan controls to view, position, and interact with nodes at different scales.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 18a.1 | With a loaded chain (e.g. from Act 18), use the **mouse wheel** to zoom out | Canvas | Canvas zooms out towards cursor position. Zoom percentage label updates (e.g. "60%"). All nodes shrink proportionally. |
| 18a.2 | Use the mouse wheel to zoom back in on a specific node cluster | Canvas | Canvas zooms in towards cursor. Nodes and edges scale up. Interactions remain accurate at the new zoom level. |
| 18a.3 | Click the **Fit View** button (fit_screen icon) in the top-right controls | Canvas | All nodes fit within the viewport with padding. Zoom and pan adjust automatically. |
| 18a.4 | Click the **Pan toggle** button (hand icon) | Canvas controls | Button highlights cyan. Cursor changes to grab. |
| 18a.5 | Click and drag on the empty canvas to pan | Canvas | Canvas pans smoothly. Cursor shows grabbing during drag. |
| 18a.6 | Click the Pan toggle again to deactivate | Canvas controls | Button de-highlights. Normal cursor restored. |
| 18a.7 | Hold **Shift** and drag on empty canvas (alternative pan) | Canvas | Canvas pans without needing the toggle button active. |
| 18a.8 | While zoomed out, drag a node to reposition it | Canvas | Node drags correctly at the current zoom level — no coordinate drift. |
| 18a.9 | While zoomed in, draw a new edge between two nodes | Canvas | Edge follows the cursor accurately. Bezier preview line snaps to ports. Connection completes correctly. |
| 18a.10 | Click **Clear** | Toolbar | All nodes removed. Zoom and pan reset to defaults (100%, centered). |

**Pass criteria:** Zoom (15%–200%) works via mouse wheel and buttons. Pan works via toggle, middle-mouse, and shift+drag. Fit View auto-sizes viewport. All interactions (drag, drop, edge draw, double-click) use correct canvas coordinates at any zoom/pan level. Clear resets zoom/pan state.

---

### Act 19: Edit an Existing Chain in Studio (Bidirectional)

**Goal:** Open a chain created via the Pipelines tab in the visual Studio editor, modify it, and verify changes persist.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 19.1 | Go to **Agents** → **Pipelines** sub-tab | Agent sub-tabs | Workflow chains list visible. |
| 19.2 | Find a chain card (e.g. "Security Audit Pipeline" from Act 12) and click the **"Studio"** button on it | Chain card | Studio view opens with the chain loaded: nodes auto-positioned vertically, edges connecting sequential steps, all properties filled. |
| 19.3 | Click a node and expand the **Advanced Options** section in properties | Properties panel | Condition, Branch To, and Parallel Group fields appear in a collapsible section. |
| 19.4 | Set a Condition on a step: `secrets_scan:files_searched not_empty` | Properties panel | Condition badge (amber ⚡) appears on the node. |
| 19.5 | Set Branch To = `agent_system` (if condition fails, branch to system agent) | Properties panel | Branch indicator appears on the node. |
| 19.6 | **Reposition** nodes by dragging them to new locations on the canvas | Canvas | Nodes move smoothly. Edges follow. |
| 19.7 | Click **Save** | Toolbar | Chain updated. Version increments. |
| 19.8 | Switch back to **Agents** → **Pipelines** | Nav bar | Chain card now shows updated version number and condition/branch badges in the flow visualization. |

**Pass criteria:** Chains created via API load correctly in Studio. Edits in Studio persist back to the chain. Version increments on save. Badges visible in both views.

---

### Act 19a: Chain-to-Chain Composition in Studio

**Goal:** Build a parent pipeline that references other workflow chains as sub-steps — composing chains into larger workflows.

> **Background:** Chain-to-chain composition lets you treat existing workflow chains as reusable building blocks. A parent chain can embed a sub-chain step that, at execution time, recursively runs the child chain (max depth 5, with cycle detection). In Studio, chain steps appear as rose-colored nodes with a link icon.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 19a.1 | Ensure at least 2 workflow chains exist (e.g. "code-review" and "security-audit" from templates in Act 11–12). If not, create them from templates in the **Pipelines** tab. | Pipelines tab | At least 2 chains visible in the chain list. |
| 19a.2 | Open **Studio** (`Ctrl+6`). Clear the canvas if needed. | Studio | Empty canvas ready. |
| 19a.3 | Click the **Chains** tab (4th tab) in the palette sidebar. | Palette | Chain palette appears showing all existing workflow chains as rose-colored draggable items with link icons and step counts. |
| 19a.4 | Drag a chain (e.g. "code-review") from the palette onto the canvas. | Canvas | A chain-type node appears: rose-colored with a link (🔗) icon and a "chain" badge. It is visually distinct from tool nodes. |
| 19a.5 | Click the chain node to select it. Review the Properties panel. | Properties panel | Properties show: a **Chain Reference** selector dropdown listing all available chains; a read-only step list preview showing the child chain's steps; Output Key and Input From fields for data flow; Advanced Options (Condition, Branch To, Parallel Group). No tool dropdown or argument fields — chain nodes don't have their own tool. |
| 19a.6 | Change the Chain Reference to a different chain using the dropdown (e.g. "security-audit"). | Properties panel | Step list preview updates to show the new chain's steps. Description auto-updates. |
| 19a.7 | Drag a regular tool node (e.g. `filesystem.tree`) from the **Tools** palette tab onto the canvas. | Canvas | Tool node appears alongside the chain node. |
| 19a.8 | Set the tool node's **Output Key** to `tree_output`. Connect the tool node's output port to the chain node's input port. | Canvas + Properties | Edge drawn. Chain node's Input From shows `tree_output`. Data flows from the tool step into the sub-chain. |
| 19a.9 | Set the chain node's **Output Key** to `audit_result`. Add another tool node (e.g. `git.status`) and set its **Input From** to `audit_result`. Connect the chain node's output port to the git.status input port. | Canvas | Three-node pipeline: tool → chain → tool. The chain node bridges two regular tool steps. |
| 19a.10 | Click **Save**. Name the chain "Composite Pipeline". | Toolbar | Chain saved via API. The serialized steps include `step_type: "chain"` and `chain_id` for the chain node. |
| 19a.11 | Click **Execute** on the saved chain. | Toolbar | Execution runs: (1) `filesystem.tree` executes, (2) the sub-chain executes recursively (all its internal steps run), (3) `git.status` executes. Results tray shows output from all steps including the sub-chain's summarized output. |
| 19a.12 | Try composing with a deeper chain: edit the sub-chain to itself reference another chain. Verify that execution depth is limited to 5 and cycles are detected. | Studio + Execute | If depth exceeds 5, execution returns a depth-limit error. If a chain references itself (directly or indirectly), execution returns a cycle-detection error. |

**Pass criteria:** Chain palette shows existing chains. Chain nodes are visually distinct (rose, link icon). Properties show chain selector and step preview. Serialization includes step_type and chain_id. Execution recursively runs sub-chains. Depth limit (5) and cycle detection prevent infinite loops.

---

### Act 19b: Studio Dynamic Argument Schemas

**Goal:** Verify that the Studio properties panel generates smart form fields for both native and MCP tools, with contextual help.

> **Background:** The Studio smart argument builder maps known tools to typed form fields (text, number, checkbox, select, textarea) via `_TOOL_ARG_SCHEMAS` covering 30+ tools. For MCP tools without static schemas, `_studioBuildDynamicSchema()` fetches the ToolSpec from the API and generates fields dynamically from its parameter definitions.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 19b.1 | Open **Studio** (`Ctrl+6`). Add a **`filesystem.grep`** node. | Canvas + Properties | Properties panel shows smart arg fields: **Query** (text, required), **Path** (text), **Pattern** (text), **Max Results** (number). Each field has a placeholder and hint text. |
| 19b.2 | Add a **`git.commit`** node. Click to select. | Properties | Smart arg fields: **Message** (text, required), **All** (checkbox for `-a` flag), **CWD** (text). |
| 19b.3 | Add a **`shell.run_safe`** node. Click to select. | Properties | Smart arg field: **Command** (text, required). |
| 19b.4 | Click the **ℹ️** icon next to any field label (e.g. "Query" on grep). | Tooltip | Contextual tooltip appears explaining the field's purpose, format, and example usage. |
| 19b.5 | Click the **JSON/Form** toggle button on any node's properties. | Properties panel | Switches between structured form fields and a raw JSON textarea. Values transfer between modes — edit in JSON, switch back to form, fields populate correctly. |
| 19b.6 | If an MCP server is connected, add an MCP tool node (e.g. `mcp.fetch.fetch`). | Properties | Studio detects the `mcp.` prefix, fetches the ToolSpec from `/tools/mcp.fetch.fetch`, and generates dynamic form fields from the tool's parameter schema. Fields show types inferred from the ToolSpec (text for strings, number for integers). |
| 19b.7 | Expand the **Data Flow** section on any node. | Properties | Output Key and Input From fields with clickable suggestions showing available output keys from other nodes for quick wiring. |
| 19b.8 | Expand the **Advanced Options** section. | Properties | Condition, Branch To, and Parallel Group fields grouped under a collapsible section with condition format documentation inline (`output_key:field op value`). |
| 19b.9 | Click the **?** help button in the properties sidebar. | Help panel | Collapsible inline help guide with 5 sections: Getting Started, Data Flow, Arguments, Advanced Features, Keyboard Shortcuts. |

**Pass criteria:** Native tools show typed form fields from static schemas. MCP tools show dynamically generated fields from ToolSpec. Tooltips provide contextual help. JSON/Form toggle preserves values. Help guide accessible.

---

## Part IV — MCP Integration

### Act 20: Register and Connect an MCP Server

**Goal:** Register an MCP server, connect it, and discover its tools — all through the UI.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 20.1 | Click **MCP** in the nav bar | Nav bar | MCP Protocol view opens with two sub-tabs: **Servers** and **Tools**. |
| 20.2 | In the **Servers** tab, review the pre-configured default servers | Servers tab | 5 default MCP servers listed: sequential-thinking, memory, fetch, github, sqlite. Each shows name, transport, enabled status, and auto_connect flag. |
| 20.3 | Click the **Connect** button on the **"sequential-thinking"** server | Server card | Server connects. Status changes to connected (green indicator). Tools discovered count appears on the card. |
| 20.4 | Click the **Connect** button on the **"memory"** server | Server card | Memory server connects. Tools registered. |
| 20.5 | Click the **Connect** button on the **"fetch"** server | Server card | Fetch server connects. |
| 20.6 | Switch to the **Tools** sub-tab | MCP sub-tabs | Grid of all discovered MCP tools appears. Each card shows: tool name (namespaced as `mcp.<server>.<tool>`), description, parameters, risk level badge, and source server. |
| 20.7 | Count the MCP tools — should be 3+ per server | Tools tab | Tools from all connected servers visible with their parameter schemas. |

**Pass criteria:** MCP servers connect successfully. Discovered tools listed with correct namespacing. Tools show parameters and risk levels.

---

### Act 21: Register a Custom MCP Server

**Goal:** Add a new MCP server (filesystem) and see its tools integrated into Machina OS.

> **Requires:** Node.js / npx installed.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 21.1 | In the **Servers** tab, fill the registration form: Name = `project-files`, Transport = `stdio`, Command = `npx` (or full npx path), Args = `-y, @modelcontextprotocol/server-filesystem, .` | Servers tab | Form populated with stdio transport details. |
| 21.2 | Click **Register** | Servers tab | New server card appears: "project-files" with transport = stdio, status = disconnected. |
| 21.3 | Click **Connect** on the new server card | Server card | Server starts as a subprocess. Handshake completes. Tools discovered count appears (typically 11-14 filesystem tools). |
| 21.4 | Switch to the **Tools** tab | MCP sub-tabs | New tools appear: `mcp.project-files.read_file`, `mcp.project-files.list_directory`, `mcp.project-files.search_files`, etc. Each with parameter details. |
| 21.5 | Go to **Chat** (`Ctrl+2`). Type `list files using mcp.project-files.list_directory` | Neural Link | Plan card appears using the MCP tool. Real directory listing returned from the MCP server. |
| 21.6 | Return to **MCP** → **Servers**. Click **Disconnect** on project-files, then **Delete** | Server card | Server disconnected and removed. Its tools disappear from the Tools tab. |

**Pass criteria:** Custom MCP server registers, connects, discovers tools. MCP tools usable from chat. Cleanup removes server and tools.

---

### Act 22: MCP Tools in Workflow Chains

**Goal:** Build a workflow chain that mixes native Machina tools with MCP-bridged tools.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 22.1 | Ensure at least one MCP server is connected (e.g. `fetch` or `memory` from Default Servers) | MCP view → Server Registry | Server shows green **Connected** dot. Tools visible in Discovered Tools sub-tab. |
| 22.2 | Go to **Studio** (`Ctrl+6`) | Nav bar | Studio canvas ready with empty workspace. |
| 22.3 | From the **Tools** palette, drag `filesystem.tree` onto the canvas | Canvas | Native tool node appears. |
| 22.4 | From the palette, scroll to the `mcp.*` section and drag an MCP tool onto the canvas. Use whichever MCP server is connected: `mcp.fetch.fetch` (if fetch server connected) or `mcp.memory.create_entities` (if memory server connected) | Canvas | MCP tool node appears alongside the native node. Both look identical in Studio — MCP tools are first-class. |
| 22.5 | Drag `git.status` onto the canvas | Canvas | Third node on canvas. |
| 22.6 | **Configure each node** in the Properties panel (click a node to select it): | Properties panel | All three nodes fully configured — see sub-steps below. |
| | **Node 1 — `filesystem.tree`:** | | |
| | → Set **Tool** dropdown to `filesystem.tree` (should already be set) | | Tool selected. |
| | → In the **Arguments** section, set the `path` field to `.` (current workspace) | | Path argument filled. |
| | → Set the `depth` field to `2` | | Depth argument filled. |
| | → In the **Data Flow** section, set **Output Key** to `project_tree` | | Output key badge appears on the node. |
| | **Node 2 — MCP tool** (example: `mcp.fetch.fetch`): | | |
| | → Click the MCP node to select it. Verify the **Tool** dropdown shows the MCP tool name. | | MCP tool selected in dropdown. |
| | → In **Arguments**: if using `mcp.fetch.fetch`, type the URL in the `url` field (e.g. `https://example.com`). If using `mcp.memory.create_entities`, type a JSON array in the `entities` field (e.g. `[{"name":"test","entityType":"note","observations":["demo observation"]}]`). For other MCP tools, fill in whichever fields the smart arg builder shows. | | Arguments populated. If the tool has no smart arg schema, toggle to **JSON mode** and enter raw `{"key": "value"}`. |
| | → Set **Output Key** to `mcp_result` | | Output key badge appears. |
| | → Set **Input From** to `project_tree` (click the suggestion or type it) — this wires the output of Node 1 into Node 2 as context | | Input-from badge appears. The node now depends on Node 1. |
| | **Node 3 — `git.status`:** | | |
| | → Click the git.status node to select it. | | Node selected. |
| | → In **Arguments**, leave the `cwd` field empty (defaults to current workspace) or set it to `.` | | Arguments set. |
| | → Set **Output Key** to `repo_status` | | Output key badge appears. |
| 22.7 | Connect nodes: click the **output port** (right side) of the `filesystem.tree` node and drag to the **input port** (left side) of the MCP tool node. Then connect the MCP tool node's output port to `git.status`'s input port. | Canvas | Two edges drawn: `filesystem.tree` → MCP tool → `git.status`. The flow shows a mixed native + MCP pipeline. Cubic Bezier curves connect the ports. |
| 22.8 | Name the chain `MCP-Enhanced Scan`, click **Save**, then **Execute** | Toolbar | Chain executes. Results show output from both native and MCP tools in the same pipeline. The results tray displays 3 step results with duration metrics. |

**Pass criteria:** Native and MCP tools coexist in the same workflow chain. Both execute successfully. Studio treats MCP tools like native ones.

---

### Act 22a: MCP Smart Registration Builder

**Goal:** Use the Quick Pick panel and smart auto-detection to register MCP servers faster — the UI recognizes known packages and auto-fills configuration.

> **Background:** The MCP view includes a Quick Pick panel with 14 curated npx MCP packages. When the user types a recognized package name in the Name or Command fields, the system auto-detects the match and highlights the corresponding Quick Pick card, auto-filling the command, args, and env fields.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 22a.1 | Go to **MCP** → **Servers** tab. Locate the **Quick Pick** panel below the registration form. | MCP Servers | Quick Pick panel visible with 14 curated MCP package cards, each showing a name and short description. |
| 22a.2 | Click the **"sequential-thinking"** card in Quick Pick. | Quick Pick panel | Registration form auto-fills: Name = `sequential-thinking`, Command = `npx`, Args = `-y, @modelcontextprotocol/server-sequential-thinking`. Transport set to `stdio`. |
| 22a.3 | Clear the form. Now manually type `github` in the **Name** field. | Name input | Smart detection activates: the **"github"** Quick Pick card highlights (ring indicator). A hint appears suggesting the recognized package. |
| 22a.4 | Click the highlighted **"github"** card or press the auto-fill hint. | Quick Pick / Form | Form auto-fills: Name = `github`, Command = `npx`, Args = `-y, @modelcontextprotocol/server-github`. Env field shows `GITHUB_PERSONAL_ACCESS_TOKEN` as required. |
| 22a.5 | Clear the form. Type `npx -y @anthropic-ai/mcp-server-sqlite` in the **Command** field. | Command input | Smart detection scans the command text and recognizes the `sqlite` package pattern. The **"sqlite"** Quick Pick card highlights. |
| 22a.6 | Click the highlighted card. | Quick Pick | Remaining fields auto-fill (args, env hints for `--db-path`). |
| 22a.7 | Clear the form. Click a Quick Pick card for a package requiring env vars (e.g. **"brave-search"**). | Quick Pick | Form fills including env var hint: `BRAVE_API_KEY`. The env field pre-populates with the variable name (value left blank for user to fill). |
| 22a.8 | Click **Register** without filling the env var value. | Register button | Server registers with empty env var. Connecting will fail gracefully (the server needs the API key at runtime). |
| 22a.9 | Delete the test server. Try typing `puppeteer` in the Name field. | Name input | The **"puppeteer"** card highlights. Auto-fill provides the correct npx package name and args. |

**Pass criteria:** Quick Pick panel shows 14 curated packages. Clicking a card auto-fills the form. Typing recognized names in Name/Command/Args triggers smart detection with highlighted cards. Env vars pre-populate for packages that need them.

---

## Part V — Complex End-to-End Scenarios

### Act 23: Full Release Readiness Assessment

**Goal:** Assemble a specialist team from templates, build a multi-phase parallel pipeline, execute it, and review comprehensive results.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 23.1 | Go to **Agents** → **Fleet**. Click **"From Template"** → create **code-reviewer** | Fleet tab | Code Reviewer agent created. |
| 23.2 | Click **"From Template"** again → create **security-auditor** | Fleet tab | Security Auditor agent created. |
| 23.3 | Create **test-engineer** from template | Fleet tab | Test Engineer created. |
| 23.4 | Create **release-manager** from template | Fleet tab | Release Manager created. Fleet now has 4 new specialist agents (10+ total). Status bar updates. |
| 23.5 | Go to **Studio** (`Ctrl+6`). Build an 8-step pipeline called `Release Readiness v1.0` with these steps: | Canvas | Steps added one by one via drag-and-drop. |
| | — (1) `filesystem.tree` (code-reviewer agent), Output Key = `project_structure`, Parallel Group = `analysis` | | |
| | — (2) `filesystem.grep` query=`TODO\|FIXME\|HACK` (code-reviewer), Output = `code_markers`, Parallel Group = `analysis` | | |
| | — (3) `filesystem.grep` query=`api_key\|secret\|password` (security-auditor), Output = `secrets_scan`, Parallel Group = `analysis` | | |
| | — (4) `filesystem.search` pattern=`test_*.py` (test-engineer), Output = `test_files`, Parallel Group = `analysis` | | |
| | — (5) `git.status` (release-manager), Output = `git_state` | | |
| | — (6) `git.log` limit=20 (release-manager), Output = `recent_commits`, Input From = `git_state` | | |
| | — (7) `system.memory` (agent_system), Output = `memory_state`, Parallel Group = `resources` | | |
| | — (8) `system.disk` path=`.` (agent_system), Output = `disk_state`, Parallel Group = `resources` | | |
| 23.6 | Connect nodes where data flows: tree→grep (markers), git.status→git.log | Canvas | Edges drawn between dependent nodes. |
| 23.7 | Click **Optimize** | Toolbar | System detects 2 parallel groups: "analysis" (steps 1-4 concurrent) and "resources" (steps 7-8 concurrent). Toast confirms. |
| 23.8 | Click **Save** then **Debug** (🐛) | Toolbar | Debug execution starts. Canvas lights up: all 4 "analysis" nodes pulse amber simultaneously → green ✓. Then sequential steps. Then "resources" nodes pulse together → green ✓. |
| 23.9 | Review the results tray | Results tray | 8 results with real data: project tree, TODO markers, secret scan hits, test file list, git status, commit log, memory stats, disk usage. Duration per step. |
| 23.10 | Go to **Agents** → **Performance** sub-tab | Agent sub-tabs | The specialist agents now show execution metrics (1 successful tool invocation each). Capability confidence updated. |
| 23.11 | *(Cleanup)* Go to **Fleet**, delete the 4 specialist agents via the delete button on each card | Fleet tab | Agents removed. Fleet count returns to baseline. |

**Pass criteria:** 4 specialist agents created from templates. 8-step pipeline with 2 parallel groups. Debug mode shows concurrent execution visually. All steps return real workspace data. Performance metrics updated.

---

### Act 24: Incident Response Simulation

**Goal:** Simulate a production incident using collaboration sessions, task queues, broadcasts, and the communication graph.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 24.1 | Go to **Agents** → **Coordination**. Create a **Collaboration Session**: Task ID = `incident_2024_memory_leak`, Participants = `agent_filesystem, agent_git, agent_system` | Coordination tab | Session created with 3 participants. |
| 24.2 | Add context to the collaboration: Key = `symptom`, Value = `RSS memory growing 2MB/hour since last deploy` | Session detail | Context key added. |
| 24.3 | Scroll to **Agent Task Queue**. Enqueue: Agent = `agent_system`, Tool = `system.memory`, Priority = 1 | Task Queue | High-priority memory check queued. |
| 24.4 | Enqueue: Agent = `agent_system`, Tool = `system.disk`, Priority = 1 | Task Queue | Disk check queued. |
| 24.5 | Enqueue: Agent = `agent_git`, Tool = `git.log` (limit=10), Priority = 2 | Task Queue | Git history check queued. |
| 24.6 | Enqueue: Agent = `agent_filesystem`, Tool = `filesystem.grep` (query=`error\|exception\|traceback`), Priority = 1 | Task Queue | Error pattern scan queued. |
| 24.7 | Click **Auto-Execute All** for each agent (system, git, filesystem) | Task Queue | All tasks execute in priority order. Results show: memory usage, disk stats, recent commits, error pattern matches. |
| 24.8 | Add the findings as collaboration context: `system_health` = `Normal`, `recent_changes` = `10 commits reviewed`, `error_patterns` = `Concentrated in core/events/` | Session detail | 4 context entries now. |
| 24.9 | Create a **Broadcast Query**: From = `orchestrator`, Question = `Root cause assessment?`, Targets = `agent_system, agent_git, agent_filesystem` | Broadcast panel | Broadcast created. |
| 24.10 | Submit responses for each agent with assessment payloads, then **Complete** and **Aggregate** (MERGE strategy) | Broadcast card | Aggregated result shows all three agent assessments in a merged view. |
| 24.11 | **Close** the collaboration session | Session detail | Session closed with timestamp. |
| 24.12 | Switch to **Communications** sub-tab | Communications tab | The SVG graph shows all incident communication flows. Activity feed shows the full timeline of the incident response. |

**Pass criteria:** Collaboration accumulates shared context. Task queue dispatches to correct agents. Broadcast aggregates multi-agent assessments. Communication graph visualizes the entire incident flow.

---

### Act 25: Auto-Healing & Health Monitoring

**Goal:** Simulate agent degradation and observe the auto-healing system.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 25.1 | Go to **Agents** → **Monitoring** sub-tab | Agent sub-tabs | Health panel showing all agents ONLINE. |
| 25.2 | Select `agent_system` in the **Health History** dropdown | Monitoring tab | Health check history visible (may show recent successful checks). |
| 25.3 | Open a new browser tab. Navigate to: `http://127.0.0.1:8100/agents/agent_system/health/status` and POST `{"status":"DEGRADED"}` using your browser's dev tools or a REST client | API | Agent status forced to DEGRADED. |
| 25.4 | Back in the UI, refresh the **Monitoring** tab | Monitoring tab | `agent_system` now shows amber DEGRADED indicator instead of green ONLINE. |
| 25.5 | Check the **status bar** at the bottom | Status bar | Fleet summary now shows "1 degraded" instead of all online. |
| 25.6 | Go to **Pipelines**. Execute a chain that uses `agent_system` tools | Pipelines tab | System may attempt auto-healing: rerouting work to a healthy alternative agent, or executing with degraded agent (still functional). |
| 25.7 | POST to `http://127.0.0.1:8100/agents/agent_system/auto-heal` to trigger manual auto-heal | API | System attempts to find a healthy replacement agent. |
| 25.8 | POST to `http://127.0.0.1:8100/agents/agent_system/health/status` with `{"status":"ONLINE"}` to restore | API | Agent returns to ONLINE. |
| 25.9 | Check **Health History** again | Monitoring tab | History shows the DEGRADED period and recovery. |
| 25.10 | Check **Performance Trends** for agent_system | Monitoring tab | SVG chart shows the health status change reflected in the trend line. |

**Pass criteria:** Degradation reflected in UI (amber indicator, status bar update). Auto-healing attempts rerouting. Recovery restores ONLINE status. Health history records the full incident.

---

### Act 26: Pipeline Lane Builder — Visual Pipeline from Scratch

**Goal:** Use the Pipeline Lane Builder to construct a workflow chain by dragging tools into agent lanes.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 26.1 | Go to **Agents** → **Pipelines** sub-tab, scroll to the **Pipeline Lane View** | Pipelines tab | Horizontal agent lanes visible (if chains exist with agent assignments). |
| 26.2 | Click the **"New from Lanes"** button | Lane view | Lane Builder mode activates: tool palette appears on the left with a filter field. Empty agent lanes ready for construction. |
| 26.3 | In the **tool palette**, type `filesystem` to filter | Palette | Only filesystem tools shown in the draggable list. |
| 26.4 | **Drag** `filesystem.tree` into the `agent_filesystem` lane | Agent lane | Tool badge appears in the filesystem agent's lane. |
| 26.5 | **Drag** `filesystem.grep` into the same lane | Agent lane | Second tool in the filesystem lane. |
| 26.6 | Clear the filter, type `git`. **Drag** `git.status` into the `agent_git` lane | Agent lane | Tool in the git agent's lane. |
| 26.7 | **Drag** `git.log` into the git lane | Agent lane | Two tools in git lane, two in filesystem lane. |
| 26.8 | **Drag** `system.info` into the `agent_system` lane | Agent lane | Tool in system lane. Visual pipeline spans 3 agent lanes. |
| 26.9 | Enter Chain Name = `Lane-Built Pipeline`, Description = `Created via visual lane builder` | Form fields | Name and description set. |
| 26.10 | Click **Create Chain** | Lane Builder | Chain created from the lane contents. Toast confirms. Chain appears in the Workflow Chains list with 5 steps across 3 agents. |

**Pass criteria:** Lane Builder allows visual construction by dragging tools into agent-specific lanes. Created chain matches the lane layout with correct agent assignments.

---

## Part VI — Orchestration Strategies

### Act 27: Compare Orchestration Strategies

**Goal:** Switch between orchestration strategies and observe how agent selection behavior changes.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 27.1 | Go to **Agents** → **Fleet** sub-tab. Find the **Orchestration** panel (or a dedicated strategy selector) | Fleet tab | Current strategy shown (default: SINGLE). Dropdown/selector for strategy. |
| 27.2 | Set strategy to **SINGLE** | Orchestration panel | Strategy saved. Toast confirms. |
| 27.3 | Go to **Chat** (`Ctrl+2`). Type `list files in current directory` | Neural Link | Executes using the first matching agent. Check the plan card's delegate_to field. |
| 27.4 | Go back to Agents. Change strategy to **CAPABILITY_SCORE** | Orchestration panel | Strategy updated. |
| 27.5 | In Chat, type `list files in current directory` again | Neural Link | May route to a different agent (the one with highest capability confidence for filesystem.list). |
| 27.6 | Change strategy to **FALLBACK** with max attempts = 3 | Orchestration panel | Fallback configuration saved. |
| 27.7 | In Chat, type `list files in current directory` | Neural Link | Uses first matching agent. If it were to fail, system would try alternatives (up to 3 attempts). |
| 27.8 | Set strategy to **PIPELINE** with pipeline_pass_output = true | Orchestration panel | Pipeline mode active. |
| 27.9 | Reset to **SINGLE** when done | Orchestration panel | Default restored. |

**Pass criteria:** Strategy changes are persisted and affect agent selection. Different strategies may route the same task to different agents.

---

### Act 28: Smart Task Scheduling

**Goal:** Let the system automatically pick the best agent for a task based on capability confidence.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 28.1 | Go to **Agents** → **Coordination** sub-tab. Find the **Smart Task Scheduling** panel | Coordination tab | Schedule form with tool selector, arguments, and priority. |
| 28.2 | Schedule: Tool = `filesystem.list`, Args = `{"path": "."}`, Priority = 1 | Schedule form | Click Schedule. Result shows: auto-routed to the best agent (e.g. agent_filesystem) with confidence score. Task enqueued. |
| 28.3 | Schedule: Tool = `git.status`, Args = `{"cwd": "."}`, Priority = 1 | Schedule form | Auto-routed to agent_git with confidence. |
| 28.4 | Schedule: Tool = `system.info`, Args = `{}`, Priority = 2 | Schedule form | Auto-routed to agent_system. |
| 28.5 | Go to the **Task Queue** and click **⚡ Auto-Execute** on each scheduled task | Task Queue | All tasks execute with real results. The system chose the optimal agent for each. |

**Pass criteria:** Smart scheduling picks the best agent per tool based on capability confidence. Tasks execute successfully through the auto-selected agents.

---

## Smoke Test Checklist

After completing the acts, verify system health:

| # | Check | Where | Expected |
|---|-------|-------|----------|
| S.1 | Fleet agents all ONLINE | Agents → Monitoring | Green dots for all agents |
| S.2 | Status bar shows correct counts | Bottom bar | online count matches fleet size, 0 degraded |
| S.3 | Chain templates ≥ 35 | Pipelines → Use Template | 35+ templates in picker |
| S.4 | Agent templates ≥ 21 | Fleet → From Template | 21+ blueprints in picker |
| S.5 | Workflow chains persist | Pipelines | All created chains visible after page refresh |
| S.6 | Execution history recorded | Pipelines → Execution History | Entries for all executed chains |
| S.7 | Communication graph populated | Communications | Edges between agents from acts 3-10 |
| S.8 | MCP tools discoverable | MCP → Tools | Tools from connected servers shown |
| S.9 | Studio loads chains | Studio → Open Chain | Saved chains appear in picker |
| S.10 | Performance data updated | Performance sub-tab | Agents that executed tools show metrics |

---

## Quick Reference: Key UI Locations

| Feature | Navigation | Shortcut |
|---------|-----------|----------|
| Agent Fleet | Agents → Fleet sub-tab | Ctrl+7 |
| Consensus / Negotiations / Handoffs | Agents → Coordination sub-tab | — |
| Agent Performance | Agents → Performance sub-tab | — |
| Health / Trends / Discovery | Agents → Monitoring sub-tab | — |
| Workflow Chains / Lane View | Agents → Pipelines sub-tab | — |
| Communication Graph / Activity Feed | Agents → Communications sub-tab | — |
| Workflow Studio | Studio view | Ctrl+6 |
| MCP Servers & Tools | MCP view | — |
| Chat / Neural Link | Chat view | Ctrl+2 |
| Home Dashboard | Home view | Ctrl+1 |

---

## Template Quick Reference

### Chain Templates (35) — Most Useful for Demos

| Template | Steps | Best For |
|----------|-------|----------|
| `pr-readiness-check` | 5 | Pre-merge validation |
| `security-deep-scan` | 5 | Comprehensive vulnerability scan |
| `code-review` | 4 | Quick code quality check |
| `deploy-check` | 3 | Pre-deployment resource check |
| `release-readiness` | 4 | Pre-release comprehensive check |
| `git-hygiene` | 5 | Branch/stash/commit health |
| `code-quality-scan` | 4 | Lint suppressions, debug stmts |
| `hotfix-workflow` | 4 | Emergency bug fix flow |
| `test-suite-check` | 4 | Test infrastructure health |
| `security-audit` | 3 | Secret scanning + pattern check |

### Agent Templates (21+) — Most Useful for Demos

| Template | Capabilities | Best For |
|----------|-------------|----------|
| `code-reviewer` | filesystem.* read-only | Code analysis |
| `security-auditor` | filesystem.grep/search | Security scanning |
| `test-engineer` | filesystem.* read-only | Test analysis |
| `release-manager` | git.*, filesystem.read | Release prep |
| `devops` | system.*, git.*, shell.run_safe | Health checks |
| `debugger` | filesystem.*, system.*, process.* | Incident response |
| `sre-agent` | system.*, process.* | Monitoring |

---

*Last updated: April 2026 · Machina OS v0.2.x · 2221+ tests*
