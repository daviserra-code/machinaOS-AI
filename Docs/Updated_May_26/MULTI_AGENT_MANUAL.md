# Machina OS — Multi-Agent System Manual

> A comprehensive guide to the multi-agent coordination features of Machina OS, with detailed examples and demo scenarios.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Agent Definitions & Fleet](#2-agent-definitions--fleet)
3. [Orchestration Strategies](#3-orchestration-strategies)
4. [Delegation & Delegation Chains](#4-delegation--delegation-chains)
5. [Consensus Decision Making](#5-consensus-decision-making)
6. [Negotiation Protocol](#6-negotiation-protocol)
7. [Task Handoff Protocol](#7-task-handoff-protocol)
8. [Agent Workflow Chains](#8-agent-workflow-chains)
9. [Capability Learning & Reputation](#9-capability-learning--reputation)
10. [Agent Health Monitoring](#10-agent-health-monitoring)
11. [Broadcast Queries & Aggregation](#11-broadcast-queries--aggregation)
12. [Collaboration Sessions](#12-collaboration-sessions)
13. [Agent Request/Response Protocol](#13-agent-requestresponse-protocol)
14. [Agent Task Queue](#14-agent-task-queue)
15. [Capability Discovery & Performance](#15-capability-discovery--performance)
16. [Agent Memory Scoping](#16-agent-memory-scoping)
17. [Agent Communications Dashboard](#17-agent-communications-dashboard)
18. [Pipeline Lane View](#18-pipeline-lane-view)
19. [Agent Blueprint Templates](#19-agent-blueprint-templates)
20. [Workflow Studio (Visual Editor)](#20-workflow-studio-visual-editor)
21. [Demo Storyboard — Multi-Agent Scenarios](#21-demo-storyboard--multi-agent-scenarios)
22. [New Tools (Sprint 58)](#22-new-tools-sprint-58)
23. [GitHub Integration](#23-github-integration)
24. [Security Center](#24-security-center)
25. [MCP Protocol Support](#25-mcp-protocol-support)
26. [Context Directory](#26-context-directory)
27. [Neural Link UI Enhancements](#27-neural-link-ui-enhancements)

---

## 1. Overview

Machina OS implements a full multi-agent coordination framework where specialized agents collaborate to execute complex tasks. Instead of a single monolithic executor, the system distributes work across purpose-built agents that can:

- **Negotiate** which agent should handle a tool invocation
- **Reach consensus** on critical decisions via voting
- **Hand off** tasks between agents mid-execution
- **Learn** from execution outcomes to improve routing
- **Self-heal** when agents become degraded or unavailable
- **Collaborate** in shared sessions with common context

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     MachinaCore                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐  │
│  │ AgentPool │  │ AgentBus │  │ RuntimeExecutor       │  │
│  │ (Registry)│  │ (Comms)  │  │ (Dispatch+Learning)   │  │
│  └─────┬────┘  └─────┬────┘  └──────────┬───────────┘  │
│        │              │                   │              │
│  ┌─────┴──────────────┴───────────────────┴──────────┐  │
│  │              Agent Subsystems                      │  │
│  │  Consensus | Negotiation | Handoffs | Health       │  │
│  │  Chains    | Broadcasts  | Collab   | Tasks        │  │
│  └────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Inter-Agent Communication Model

The AgentBus provides **6 communication channels**, each designed for a different interaction pattern. These protocols fire automatically during multi-agent plan execution — you don't manually send messages between agents. The Communications Dashboard (6th Agent sub-tab) provides a read-only monitoring view of all traffic.

| Channel | Pattern | Purpose | Lifecycle | Triggered By |
|---------|---------|---------|-----------|-------------|
| **Bus Messages** | Pub/sub | Low-level event transport for all agent interactions | fire-and-forget | Every protocol below emits events as side effects |
| **Agent Requests** | Point-to-point | Direct ask from Agent A to Agent B expecting a response | `PENDING → DELIVERED → RESPONDED` (or `TIMEOUT`/`FAILED`) | RuntimeExecutor when routing task steps |
| **Broadcast Queries** | One-to-many poll | Ask multiple agents a question, collect + aggregate answers | `PENDING → COLLECTING → COMPLETED` (or `EXPIRED`) | Consensus voting, capability discovery |
| **Negotiations** | Bilateral propose/counter | Resolve tool ownership when multiple agents match | `PROPOSED → COUNTERED → ACCEPTED/REJECTED/RESOLVED` | `CAPABILITY_SCORE` strategy, pipeline negotiation |
| **Handoffs** | Formal transfer | Transfer a task step between agents with preconditions | `REQUESTED → ACCEPTED → EXECUTING → COMPLETED` (or `DECLINED`/`FAILED`) | Auto-heal (degraded agent replaced), explicit delegation |
| **Collaborations** | Shared session | Multi-agent work on a common task with shared context | `create → join → set_context → close` | Complex multi-step tasks needing shared state |

**How they compose:**

1. A plan step is delegated to an agent via the **AgentPool** (strategy-based selection)
2. If multiple agents match, a **negotiation** determines the best candidate (or **consensus** if enabled)
3. If the chosen agent is degraded, **auto-heal** triggers a **handoff** to a healthy replacement
4. During execution, agents exchange data via **bus messages** (output bridging)
5. For complex tasks, agents join a **collaboration session** to share context
6. **Broadcast queries** gather information from the fleet (e.g., "which agents can handle this tool?")
7. The **task queue** buffers work items per agent with priority ordering, enabling async dequeue + auto-execute

All inter-agent traffic is visible in the Communications Dashboard: an SVG graph shows agent nodes with color-coded directed edges (cyan = request, amber = negotiation, purple = handoff, emerald = broadcast), and a unified activity feed shows all events chronologically.

### Built-in Agents

Machina OS ships with 4 pre-configured agents:

| Agent | ID | Tool Filter | Capabilities |
|-------|----|-------------|-------------|
| **Filesystem** | `agent_filesystem` | `filesystem.*` | list, read, create, delete, move, grep, semantic_search |
| **Git** | `agent_git` | `git.*` | git, git_command, clone |
| **Shell** | `agent_shell` | `shell.*`, `process.*` | shell, execute, list_processes |
| **System** | `agent_system` | `system.*` | system, system_info |

Custom agents can be created via the API or UI with arbitrary tool filters and capabilities.

---

## 2. Agent Definitions & Fleet

### Creating an Agent

Each agent is defined by:
- **agent_id**: Auto-generated with `agent_` prefix, or custom
- **name**: Human-readable display name
- **capabilities**: List of capability keywords (e.g., `["filesystem", "read", "write"]`)
- **tool_filter**: Fnmatch glob patterns determining which tools the agent can execute (e.g., `["filesystem.*", "shell.run"]`)
- **system_prompt**: Custom LLM prompt that shapes agent behaviour during planning and delegation (see [System Prompt Guide](#system-prompt-guide) below)
- **enabled**: Toggle agent on/off without deleting

#### API Example: Create Agent
```http
POST /agents
Content-Type: application/json

{
  "name": "Security Auditor",
  "description": "Specialized agent for security scanning",
  "capabilities": ["security", "audit", "scan"],
  "tool_filter": ["filesystem.read_file", "filesystem.grep", "shell.run_safe"],
  "system_prompt": "You are a security-focused code auditor. Scan for hardcoded secrets, insecure patterns, and missing access controls. Flag findings by severity (critical/high/medium/low). Prefer safe read-only operations. Never modify source files."
}
```

Response:
```json
{
  "agent_id": "agent_abc123",
  "name": "Security Auditor",
  "enabled": true,
  "tool_filter": ["filesystem.read_file", "filesystem.grep", "shell.run_safe"]
}
```

### System Prompt Guide

The `system_prompt` field is injected into the LLM at two points:

1. **Planner** — when building the agent catalog for plan generation, each agent's prompt is appended as a `Behaviour:` hint so the planner knows *how* the agent operates, not just which tools it owns.
2. **Chat** — when building the conversational system prompt, each agent's prompt is included in the `Available agents` list so the LLM can decide which agent to suggest for a task.

A well-crafted system prompt makes an agent **predictable, safe, and task-focused**.

#### The 5-Part Prompt Formula

| Part | Purpose | Example |
|------|---------|---------|
| **Role** | Declare identity | *"You are a security-focused code auditor."* |
| **Responsibilities** | What the agent does | *"Scan for hardcoded secrets, insecure patterns, and missing access controls."* |
| **Output format** | How results are presented | *"Flag findings by severity: critical, high, medium, low. Group by file."* |
| **Safety constraints** | What the agent must NOT do | *"Prefer safe read-only operations. Never modify source files."* |
| **Escalation rules** | When to defer to humans | *"If a critical finding is detected, recommend human review before proceeding."* |

#### Do / Avoid

| ✓ Do | ✗ Avoid |
|------|---------|
| Start with a clear role — *"You are a …"* | Vague instructions — *"Be helpful"* |
| List core responsibilities explicitly | Contradicting the tool filter (granting tools it can't use) |
| State safety constraints | Extremely long prompts (keep under ~300 characters) |
| Specify preferred output format | Including secrets, API keys, or credentials |
| Mention when to escalate vs handle alone | Instructions that override system safety policies |

#### Built-in Agent Prompts

All 6 built-in agents ship with safety-oriented system prompts:

| Agent | System Prompt |
|-------|---------------|
| **Filesystem** | *"You are a filesystem specialist. Navigate, read, write, and organise files safely. Verify paths before destructive operations. Prefer read-only."* |
| **Git** | *"You are a version-control specialist. Prefer non-destructive commands. Require confirmation before push or force operations."* |
| **Shell** | *"You are a shell execution specialist. Validate commands before execution. Never run destructive commands without approval."* |
| **System** | *"You are a system introspection specialist. Report metrics clearly with units. Flag anomalies."* |
| **Browser** | *"You are a browser automation specialist. Validate URLs before opening. Do not navigate to untrusted URLs without confirmation."* |
| **VS Code** | *"You are a VS Code integration specialist. Prefer read-only inspection. Do not install extensions without consent."* |

Template agents (created via "From Template") also ship with role-specific prompts that can be customized in the agent editor.

### Tool Filter Matching

Tool filters use fnmatch glob patterns:
- `filesystem.*` — matches all filesystem tools
- `shell.run` — matches only `shell.run` (exact)
- `*` — matches everything (open agent)
- `git.*` — matches `git.status`, `git.log`, `git.diff`, etc.

An agent with `tool_filter: ["filesystem.read_file", "filesystem.grep"]` will only be selected for those two specific tools.

### Fleet Summary

```http
GET /agents/summary
```
Returns:
```json
{
  "total": 5,
  "online": 4,
  "degraded": 1,
  "offline": 0,
  "top_agent": "agent_filesystem",
  "top_score": 0.95
}
```

---

## 3. Orchestration Strategies

The orchestration strategy controls how the system selects which agent handles a given tool invocation.

### Available Strategies

| Strategy | Behavior | Use Case |
|----------|----------|----------|
| **SINGLE** | First matching agent wins | Simple setups, single-agent-per-tool |
| **ROUND_ROBIN** | Rotate across matching agents | Load distribution |
| **CAPABILITY_SCORE** | Highest specificity score wins | Prefer most specialized agent |
| **FALLBACK** | Try agents in order; advance on failure | Fault tolerance |
| **PIPELINE** | Chain agents sequentially, pass output | Multi-stage processing |

### Specificity Scoring

When multiple agents can handle the same tool, specificity determines priority:
- **Exact match** (filter = `shell.run` for tool `shell.run`): score = **1.0**
- **Prefix glob** (filter = `shell.*` for tool `shell.run`): score = **0.3 + specificity**
- **Open filter** (filter = `*`): score = **0.1**

#### API Example: Set Strategy
```http
PUT /orchestration
Content-Type: application/json

{
  "strategy": "FALLBACK",
  "max_fallback_attempts": 3,
  "pipeline_pass_output": true
}
```

### Demo Scenario: Fallback in Action

1. Agent `agent_shell` is the primary handler for `shell.run`
2. Agent `agent_shell` goes OFFLINE (3+ consecutive failures)
3. A task requires `shell.run`
4. System detects OFFLINE status, skips `agent_shell`
5. Falls back to `agent_backup_shell` (if registered with matching filter)
6. Task succeeds; `agent_backup_shell` gains capability confidence

---

## 4. Delegation & Delegation Chains

### How Delegation Works

When a plan step includes `delegate_to: "agent_git"`, the RuntimeExecutor:
1. Checks if the target agent accepts the tool (`accepts_tool()`)
2. If rejected: returns `AGENT_TOOL_DENIED` error
3. If accepted: executes the tool in the agent's context
4. Records capability outcome for learning

### Delegation Chains

When agents delegate to other agents, Machina OS tracks and validates the chain:

```
agent_filesystem → agent_git → agent_shell
         ↑ chain depth = 3
```

**Safety checks:**
- **Cycle detection**: `agent_A → agent_B → agent_A` is blocked with `DELEGATION_CYCLE` error
- **Depth limit**: Maximum depth of 5 (configurable)

#### API: View Active Chains
```http
GET /agents/delegation-chains
```
Response:
```json
[
  {
    "chain_id": "dc_001",
    "path": ["agent_filesystem", "agent_git"],
    "depth": 2,
    "max_depth": 5
  }
]
```

### Demo Scenario: Cross-Agent Delegation

User says: *"Delegate to git agent to check the repository status"*

1. Intake detects "delegate to" pattern, extracts `agent_name: "git"`
2. Planner resolves agent_id `agent_git` from pool
3. Creates plan step: `{ tool: "git.status", delegate_to: "agent_git" }`
4. Executor validates agent accepts `git.status` ✓
5. Executes tool, emits `delegation_request` on agent bus
6. Records capability score for `agent_git` + `git.status`

---

## 5. Consensus Decision Making

Consensus enables multiple agents to vote on critical decisions before execution proceeds.

### How It Works

1. A consensus request is created with a **question**, **candidate agents**, and a **strategy**
2. Each candidate agent casts a vote: APPROVE, REJECT, or ABSTAIN
3. Votes can carry **weight** (0.0–1.0) and a **reason**
4. The request is **resolved** according to the chosen strategy

### Strategies

| Strategy | Resolution Rule |
|----------|----------------|
| **MAJORITY** | More approvals than rejections (weighted) |
| **UNANIMOUS** | All votes must be APPROVE |
| **WEIGHTED** | Weighted sum: approvals > rejections |

### Consensus-Aware Execution

When the RuntimeExecutor encounters a tool that matches `consensus_tool_patterns`:
1. Finds candidate agents for the tool
2. If ≥2 candidates exist, creates consensus request
3. Each agent **auto-votes** based on its capability confidence:
   - Confidence ≥ 0.3 → APPROVE (weight = confidence)
   - Confidence < 0.3 → REJECT (weight = 1 − confidence)
4. Resolves consensus:
   - **RESOLVED** → proceed with execution
   - **REJECTED** → return `CONSENSUS_REJECTED` error

### Consensus Pattern Learning

The system learns from consensus outcomes:
- After each resolution, records whether the tool was approved
- When a tool has ≥10 consensus evaluations AND >95% approval rate, **consensus is automatically skipped** for that tool
- This reduces overhead for well-established tool-agent pairings

#### API Example: Create Consensus
```http
POST /consensus
Content-Type: application/json

{
  "question": "Should we deploy the updated configuration?",
  "candidates": ["agent_filesystem", "agent_git", "agent_system"],
  "strategy": "majority",
  "min_voters": 2
}
```

#### API Example: Cast Vote
```http
POST /consensus/{request_id}/vote
Content-Type: application/json

{
  "agent_id": "agent_filesystem",
  "value": "approve",
  "weight": 0.9,
  "reason": "Configuration file changes look safe"
}
```

#### API Example: Resolve
```http
POST /consensus/{request_id}/resolve
```
Response:
```json
{
  "status": "resolved",
  "question": "Should we deploy the updated configuration?",
  "votes": {
    "agent_filesystem": { "value": "approve", "weight": 0.9 },
    "agent_git": { "value": "approve", "weight": 0.7 },
    "agent_system": { "value": "reject", "weight": 0.3 }
  }
}
```

### Demo Scenario: Multi-Agent Approval

1. User requests: *"Deploy the configuration changes"*
2. Tool `shell.run` matches consensus pattern
3. 3 agents are candidates: filesystem, git, system
4. Auto-voting:
   - `agent_filesystem`: confidence 0.85 → APPROVE (weight 0.85)
   - `agent_git`: confidence 0.6 → APPROVE (weight 0.6)
   - `agent_system`: confidence 0.2 → REJECT (weight 0.8)
5. MAJORITY strategy: weighted approvals (1.45) > rejections (0.8) → **RESOLVED**
6. Execution proceeds

---

## 6. Negotiation Protocol

Negotiation enables two agents to dispute which one should handle a tool invocation, with multi-round counter-proposals.

### Negotiation Lifecycle

```
PROPOSED → COUNTERED → (repeat) → ACCEPTED / REJECTED / RESOLVED / WITHDRAWN
```

### Priority Levels

| Level | Value | Meaning |
|-------|-------|---------|
| CRITICAL | 1 | Highest priority |
| HIGH | 2 | Important |
| NORMAL | 3 | Default |
| LOW | 4 | Best-effort |

### How It Works

1. **Initiator** proposes that a specific agent should handle a tool
2. **Responder** can:
   - **Accept**: Initiator's proposed agent wins
   - **Counter**: Suggest an alternative agent (with reason)
   - **Reject**: Neither agent gets the tool
3. Multi-round counters continue up to `max_rounds` (default 3)
4. **Auto-resolve by priority**: Lower priority value wins (tie → initiator wins)
5. **Auto-counter**: System automatically suggests the best alternative agent based on capability scores

#### API Example: Start Negotiation
```http
POST /negotiations
Content-Type: application/json

{
  "initiator": "agent_filesystem",
  "responder": "agent_shell",
  "tool": "shell.run_safe",
  "priority": 2,
  "reason": "I have better read-only shell access patterns"
}
```

#### API Example: Counter-Propose
```http
POST /negotiations/{negotiation_id}/counter
Content-Type: application/json

{
  "counter_agent": "agent_shell",
  "counter_reason": "I'm the primary shell executor with higher confidence"
}
```

#### API Example: Auto-Counter
```http
POST /negotiations/{negotiation_id}/auto-counter
```
The system picks the best alternative agent by capability confidence and automatically submits a counter-proposal.

#### API Example: Auto-Resolve by Priority
```http
POST /negotiations/{negotiation_id}/resolve
```
Compares initiator/responder priorities. Lower value wins. Ties go to the initiator.

### Demo Scenario: Agent Tool Dispute

1. `agent_filesystem` and `agent_shell` both match `shell.run_safe`
2. `agent_filesystem` proposes itself (priority HIGH=2)
3. `agent_shell` counters with itself (priority NORMAL=3)
4. Auto-resolve: HIGH (2) < NORMAL (3) → `agent_filesystem` wins
5. Winner is recorded; future routing uses this preference

### Negotiation Timeline

View the full round-by-round history of any negotiation:

```http
GET /negotiations/{negotiation_id}/timeline
```

Returns a chronological list of events:
```json
{
  "negotiation_id": "neg_abc123",
  "events": [
    { "phase": "PROPOSED", "agent": "agent_filesystem", "round": 0, "reason": "Better read-only patterns", "timestamp": "..." },
    { "phase": "COUNTERED", "agent": "agent_shell", "round": 1, "reason": "Primary shell executor", "timestamp": "..." },
    { "phase": "RESOLVED", "agent": "agent_filesystem", "round": 1, "reason": "Priority wins", "timestamp": "..." }
  ]
}
```

In the UI, the timeline is displayed as a vertical flow with phase-colored dots:
- **Cyan** = PROPOSED
- **Amber** = COUNTERED
- **Green** = ACCEPTED
- **Red** = REJECTED
- **Purple** = RESOLVED

---

## 7. Task Handoff Protocol

Handoffs allow one agent to formally transfer responsibility for a task to another agent.

### Handoff Lifecycle

```
REQUESTED → ACCEPTED → EXECUTING → COMPLETED / FAILED
                    ↘ DECLINED
REQUESTED → CANCELLED
```

### Handoff Features

- **Preconditions**: List of requirements that must be met before the handoff
- **Constraints**: Dict of operational constraints (e.g., `{ "timeout": 30000 }`)
- **Reason**: Why the handoff is being requested
- **Decline reason**: Why the target agent rejected the handoff

#### API Example: Request Handoff
```http
POST /handoffs
Content-Type: application/json

{
  "from_agent": "agent_filesystem",
  "to_agent": "agent_git",
  "tool": "git.status",
  "reason": "Need git-specific analysis of repository state",
  "preconditions": ["workspace must be a git repository"],
  "constraints": { "timeout_ms": 10000 }
}
```

#### API Example: Accept and Complete
```http
POST /handoffs/{handoff_id}/accept
# ... agent executes the work ...
POST /handoffs/{handoff_id}/complete
```

### Demo Scenario: Filesystem-to-Git Handoff

1. `agent_filesystem` is scanning a project directory
2. Discovers `.git/` directory — needs git-specific analysis
3. Creates handoff to `agent_git` with reason: "Found git repository, need status analysis"
4. `agent_git` accepts the handoff
5. `agent_git` runs `git.status`, `git.log`
6. `agent_git` completes the handoff with results
7. `agent_filesystem` receives the git analysis and continues

---

## 8. Agent Workflow Chains

Workflow chains define multi-step pipelines where different agents execute specific tools in sequence, with output passing between steps.

### Chain Step Fields

| Field | Type | Description |
|-------|------|-------------|
| `agent_id` | string | Which agent executes this step |
| `tool` | string | Tool to invoke |
| `arguments` | dict | Tool arguments |
| `description` | string | Human-readable step description |
| `output_key` | string | Key to store step output |
| `input_from` | string | Key to read prior step output from |
| `condition` | string | Conditional execution gate |
| `branch_to` | string | Alternate agent if condition fails |
| `parallel_group` | string | Group key for concurrent execution |
| `step_type` | string | `"tool"` (default) or `"chain"` for sub-chain reference |
| `chain_id` | string | Sub-chain id when `step_type="chain"` |
| `continue_on_failure` | bool | When `true`, the chain proceeds past this step on FAILED status instead of aborting (used for tolerant scan steps in audit chains). Default `false`. |

### Condition Syntax

Conditions follow the format: `output_key:field op value`

| Operator | Meaning | Example |
|----------|---------|---------|
| `==` | Equals | `scan_result:status == clean` |
| `!=` | Not equals | `scan_result:status != error` |
| `contains` | Contains substring | `scan_result:files contains .py` |
| `not_empty` | Field is not empty | `scan_result:files not_empty` |

### Cross-Agent Branching

When a condition fails and `branch_to` is set, the step is rerouted to the alternate agent instead of being skipped:

```
Step 3: agent_filesystem → filesystem.grep (condition: scan:issues == none)
        ┗ branch_to: agent_shell (if condition fails, reroute to shell agent)
```

### Parallel Execution

Steps sharing the same `parallel_group` value run concurrently:

```yaml
Step 1: filesystem.tree      (parallel_group: "init")
Step 2: git.status           (parallel_group: "init")  # runs simultaneously with Step 1
Step 3: filesystem.read_file (parallel_group: null)     # waits for group "init" to finish
```

### Built-in Chain Templates

| Template | Steps | Description |
|----------|-------|-------------|
| **code-review** | tree → git.status → grep TODO/FIXME → read README | Code quality inspection |
| **deploy-check** | git.status → git.log → system.memory → system.disk | Pre-deployment verification |
| **project-scan** | tree → search configs → git.status → system.info | Full project analysis |
| **security-audit** | grep secrets → grep insecure patterns → tree | Security scanning |
| **dependency-check** | search package.json/requirements.txt/Cargo.toml → read | Cross-language dependency review |
| **release-readiness** | grep TODO/FIXME → grep debug/console.log → system.memory → system.disk | Release blocker check |
| **onboarding-scan** | search README → search docs → search Docker → search .env | New contributor onboarding |
| **log-investigation** | grep error/exception → grep warning → git.log recent | Error pattern analysis |
| **cleanup-sweep** | search .bak/.tmp/.log → tree → system.disk | Stale artifact cleanup |
| **test-suite-check** | search test files → grep test functions → search configs | Test coverage inspection |
| **api-health-check** | grep route/endpoint → search config → search .env | API route discovery |
| **documentation-audit** | search README/CHANGELOG → grep TODO in docs → tree docs/ | Documentation gap analysis |
| **migration-check** | search schema/migration files → grep migration patterns | Database migration review |
| **ci-cd-audit** | search CI configs → search build scripts → search Dockerfile | Pipeline configuration check |
| **performance-profile** | system.memory → system.disk → system.info → grep large files → tree | Resource and performance profiling |
| **git-hygiene** | git.status → git.branch → git.stash → git.log → grep gitignore | Git repository health check |
| **env-config-audit** | search .env files → grep secrets → search configs | Environment configuration review |
| **code-quality-scan** | grep lint suppressions → grep debug statements → grep wildcards → git.diff | Code quality sweep |
| **error-investigation** | grep exceptions → grep error raises → grep log statements → git.log → system.memory | Error pattern investigation |
| **license-compliance** | search license files → grep copyright → grep attribution | License compliance audit |
| **code-review-deep** | tree → git.diff → grep patterns → read key files → git.log | Deep comprehensive code review |
| **debug-investigation** | grep exceptions → read affected files → git.log → git.diff → system.info | Full debug session workflow |
| **refactoring-analysis** | tree → grep patterns → read files → git.diff → system.disk | Refactoring opportunity scan |
| **api-design-review** | grep routes → read API files → search schemas → git.log | API design assessment |
| **security-deep-scan** | grep secrets → grep insecure patterns → grep JWT → tree → git.log | Comprehensive security audit |
| **docker-k8s-review** | search Dockerfile → search docker-compose → search k8s manifests | Container orchestration review |
| **test-coverage-analysis** | search test files → grep test functions → grep coverage configs | Test coverage assessment |
| **documentation-review** | search README → search CHANGELOG → grep TODO in docs → tree docs/ | Documentation completeness review |
| **db-optimization** | search schema files → grep queries → grep indexes → read migrations | Database optimization analysis |
| **hotfix-workflow** | grep error pattern → read affected files → git.status → git.diff | Hotfix preparation workflow |
| **pr-readiness-check** | git.status → git.diff → grep TODO → grep debug statements → system.disk | PR readiness verification |
| **changelog-generation** | git.log → git.diff → grep CHANGELOG → read README | Changelog generation workflow |
| **monorepo-scan** | tree → search package files → grep workspace configs → system.disk | Monorepo structure analysis |
| **stale-branch-cleanup** | git.branch → git.log → grep stale patterns → git.status | Stale branch identification |
| **feature-branch-setup** | git.status → git.log → git.branch → tree | Feature branch setup workflow |

#### Coworking Chain Templates (atomic)

| Template | Steps | Description |
|----------|-------|-------------|
| **morning-brief** | time.now → git.status → git.log → notes.create | Daily morning briefing note |
| **meeting-prep** | notes.search → filesystem.grep → time.now → notes.create | Gather context + draft agenda note |
| **research-capture** | clipboard.read → text.extract_urls → text.stats → notes.create | Turn clipboard content into a searchable research note |
| **knowledge-sweep** | notes.list → notes.search → text.stats | Audit the notes corpus |
| **daily-standup** | git.log → git.status → time.now → notes.create | Daily standup summary note |
| **weekly-review** | git.log (7d) → notes.list → notes.create | Weekly review note |
| **client-handoff** | tree → git.log → notes.search → notes.create | Client-ready handoff brief |

#### Composite Chain Templates (chain-to-chain)

These templates reference **other chain templates** via a `chain_template` step key. At instantiation time the bus materialises each referenced sub-chain, persists it to `chains.db`, and wires the real `chain_id` into the parent step (`step_type="chain"`). Sub-chains are visible in the Studio chain palette and can be executed independently.

| Template | Sub-chains | Description |
|----------|------------|-------------|
| **master-audit** | security-audit + dependency-check + code-quality-scan + notes.create | Full-project audit across security, deps, and quality |
| **release-master** | release-readiness + dependency-check + git-hygiene + notes.create | End-to-end release readiness sweep |
| **ops-orchestration** | deploy-check + performance-profile + log-investigation + notes.create | Ops health sweep |
| **client-onboarding-pack** | onboarding-scan + project-scan + documentation-audit + notes.create | Client-ready onboarding bundle |
| **weekly-coworking-cycle** | weekly-review + knowledge-sweep + morning-brief | Weekly coworking close-out + next-day prep |

> Composite templates are resolved recursively (`MAX_CHAIN_DEPTH=5`). Cycles and missing sub-templates degrade gracefully to a labelled `system.status` no-op so the parent chain stays valid. See `Docs/CHAIN_COMPOSITION_DEMOS.md` for walkthroughs.

#### API Example: Create Chain
```http
POST /workflow-chains
Content-Type: application/json

{
  "name": "Security Scan Pipeline",
  "description": "Multi-agent security scanning workflow",
  "steps": [
    {
      "agent_id": "agent_filesystem",
      "tool": "filesystem.tree",
      "arguments": { "path": "." },
      "description": "Map project structure",
      "output_key": "project_tree"
    },
    {
      "agent_id": "agent_filesystem",
      "tool": "filesystem.grep",
      "arguments": { "pattern": "password|secret|api_key", "path": "." },
      "description": "Scan for credential patterns",
      "output_key": "credential_scan",
      "input_from": "project_tree"
    },
    {
      "agent_id": "agent_git",
      "tool": "git.log",
      "arguments": { "count": 10 },
      "description": "Check recent commits",
      "output_key": "recent_commits",
      "parallel_group": "analysis"
    },
    {
      "agent_id": "agent_system",
      "tool": "system.info",
      "arguments": {},
      "description": "System environment check",
      "parallel_group": "analysis"
    }
  ]
}
```

#### API Example: Execute Chain
```http
POST /workflow-chains/{chain_id}/execute
```

#### API Example: Execute with Parallel Groups
```http
POST /workflow-chains/{chain_id}/execute-parallel
```

### Chain Persistence

Workflow chains are persisted to SQLite (`chains.db`) via `ChainStore`. Chains survive server restarts automatically.

- **On create/update/rollback/delete:** AgentBus auto-persists via `_persist_chain()` / `_chain_store.delete()`
- **On startup:** `_load_persisted_chains()` restores all chains from SQLite
- **Storage format:** chain_id, name, description, steps (JSON), version, version_history (JSON), created_at, updated_at

### Chain Versioning

Every workflow chain carries an immutable version history. This enables safe iteration — you can modify chains freely knowing every previous state is recoverable.

#### How It Works

1. **Creation** — a new chain starts at **version 1** with an empty `version_history`.
2. **Update** — when steps are changed (via API, UI edit, drag-and-drop reassignment, or conflict resolution), the chain:
   - Takes a **snapshot** of the current state (version number, name, steps, timestamp)
   - Appends that snapshot to `version_history`
   - Increments `version` by 1
   - Replaces steps with the new ones
   - Updates `updated_at`
3. **Rollback** — when rolling back to a target version:
   - The **current** state is snapshot-saved first (so it's never lost)
   - The chain's steps/name are restored from the target version's snapshot
   - `version` increments again (rollback is itself a new version)
   - This means rollback is **non-destructive** — you can undo a rollback

#### Version History Format

Each entry in `version_history` is a dict:
```json
{
  "version": 2,
  "name": "Pre-Commit Check",
  "steps": [ ...full step definitions... ],
  "timestamp": "2026-04-16T21:30:00"
}
```

#### What Triggers a Version Bump

| Action | Version Bumps? |
|--------|----------------|
| Create chain | No (starts at v1) |
| Edit steps via PUT API or UI | Yes |
| Drag step between lanes (Pipeline Lane View) | Yes |
| Resolve conflicts (agent reassignment) | Yes |
| Apply optimization (parallel groups) | Yes |
| Auto-assign agents | Yes |
| Rollback to previous version | Yes (new version) |
| Execute chain | No |
| Delete chain | N/A (chain removed) |

#### API

```http
# Update chain (saves snapshot, increments version)
PUT /workflow-chains/{chain_id}
Content-Type: application/json
{
  "steps": [ ...new steps... ],
  "description": "Updated scan rules"
}
# Response includes new version number

# View full version history
GET /workflow-chains/{chain_id}/versions
# Returns: list of snapshots [{version, name, steps, timestamp}, ...]

# Rollback to a specific version
POST /workflow-chains/{chain_id}/rollback
Content-Type: application/json
{ "target_version": 1 }
# Current state is saved first, then target state is restored
```

#### Example Timeline

```
v1  Chain created: steps A → B → C
v2  User edits:    steps A → B → D       (v1 snapshot saved)
v3  Auto-assign:   agent changes on B     (v2 snapshot saved)
v4  Rollback to v1: steps A → B → C       (v3 snapshot saved)
v5  User edits:    steps A → E            (v4 snapshot saved)
```

At v5, `version_history` contains snapshots for v1, v2, v3, and v4 — all recoverable.

#### UI Controls

- **History** button on chain cards → shows all past versions with timestamps
- **Rollback** button → reverts to a selected previous version
- Pipeline Lane View drag-and-drop → auto-bumps version on reassignment
- Conflict resolution → auto-bumps version when agents are reassigned

### Chain Optimization

The system can analyze dependencies and suggest parallelization:

```http
# Analyze dependencies and suggest parallel groups
POST /workflow-chains/{chain_id}/optimize

# Apply the suggested optimization
POST /workflow-chains/{chain_id}/apply-optimization
```

### Auto-Assign Agents

Let the system assign the best agent for each step based on capability confidence:

```http
POST /workflow-chains/{chain_id}/auto-assign
```

### Debug Execution (Step-by-Step SSE)

Stream chain execution step-by-step via Server-Sent Events:

```http
POST /workflow-chains/{chain_id}/execute-debug
```

Event types:
- `step_start` — `{index, tool, step_id}` before each step runs
- `step_done` — `{index, status, duration_ms, output (2000 char preview), error_code, message}` after each step
- `done` — `{status, total_steps, succeeded, failed, skipped}` when chain completes

The debug endpoint evaluates conditions, bridges outputs between steps, and breaks on first failure.

### Pipeline Negotiation

Agents negotiate who handles each step:

```http
POST /workflow-chains/{chain_id}/negotiate
```
Returns assignments with confidence scores and any conflicts (ties):
```json
{
  "assignments": [
    { "step_index": 0, "tool": "filesystem.tree", "agent_id": "agent_filesystem", "confidence": 0.95 }
  ],
  "conflicts": [
    { "step_index": 2, "tool": "shell.run_safe", "tied_agents": ["agent_shell", "agent_filesystem"], "confidence": 0.5 }
  ]
}
```

### Bulk Pipeline Negotiation

Negotiate across all existing workflow chains at once:

```http
POST /workflow-chains/negotiate-all
```
Returns per-chain results:
```json
[
  {
    "chain_id": "wfc_abc123",
    "chain_name": "Security Scan",
    "assignments": [...],
    "conflicts": [...]
  }
]
```

The UI provides a **Negotiate All** button on the Workflow Chains panel that runs this across all chains and reports the total conflict count via toast notification.

### Chain Execution History & Replay

Every chain execution is recorded:

```http
# List executions
GET /chain-executions

# Replay a previous execution (optionally override arguments)
POST /chain-executions/{execution_id}/replay
Content-Type: application/json
{ "override_arguments": { "step_0": { "path": "/new/path" } } }
```

### Demo Scenario: Multi-Agent Pipeline

1. Create a "Deploy Readiness Check" chain with 4 steps:
   - Step 1: `agent_git` → `git.status` (output_key: "git_state")
   - Step 2: `agent_git` → `git.log` (output_key: "recent_changes", parallel_group: "check")
   - Step 3: `agent_system` → `system.memory` (output_key: "mem_check", parallel_group: "check")
   - Step 4: `agent_system` → `system.disk` (condition: `mem_check:available_mb != 0`)
2. Execute the chain with parallel groups
3. Steps 2 and 3 run concurrently (both in group "check")
4. Step 4 only runs if the memory check returned data
5. View the execution record showing ✓ ✗ ⊘ per step

---

## 9. Capability Learning & Reputation

### Capability Learning

Every time an agent executes a tool, the outcome is recorded:

- **Success**: Increments success counter, records duration
- **Failure**: Increments failure counter, records error code and duration
- **Confidence formula**: `success_rate × min(1.0, sample_size / 20)`
  - With 0 samples: neutral prior of 0.5
  - Needs 20+ samples for full confidence

```http
GET /agents/agent_filesystem/capabilities
```
Response:
```json
[
  {
    "agent_id": "agent_filesystem",
    "tool": "filesystem.list",
    "successes": 45,
    "failures": 2,
    "confidence": 0.94,
    "avg_duration_ms": 23,
    "last_error_code": "TIMEOUT"
  }
]
```

### Agent Reputation

Cross-task aggregation of agent performance:

- **reputation_score** = `(0.4 × lifetime_success_rate + 0.6 × recent_success_rate) × sample_confidence`
- **recent_outcomes**: Rolling window of last 50 outcomes (recency bias)
- **tools_used**: Dictionary of tool → invocation count

```http
GET /agents/agent_filesystem/reputation
```
Response:
```json
{
  "agent_id": "agent_filesystem",
  "reputation_score": 0.92,
  "success_rate": 0.96,
  "recent_success_rate": 0.98,
  "sample_size": 47,
  "tools_used": {
    "filesystem.list": 20,
    "filesystem.read_file": 15,
    "filesystem.grep": 12
  }
}
```

### Impact on Routing

- **CAPABILITY_SCORE** strategy uses confidence to select agents
- **best_agent_for_tool()** picks the agent with highest confidence
- **Auto-voting** in consensus uses confidence as vote weight
- **Auto-counter** in negotiations selects alternatives by confidence

---

## 10. Agent Health Monitoring

### Health States

| Status | Meaning | Visual |
|--------|---------|--------|
| **ONLINE** | Agent is healthy and responsive | 🟢 Green |
| **DEGRADED** | Agent has intermittent issues | 🟡 Amber |
| **OFFLINE** | Agent is unresponsive | 🔴 Red |

### Automatic State Transitions

- **3 consecutive failures** → DEGRADED
- **6 consecutive failures** (2× threshold) → OFFLINE
- **3 consecutive successes** after degradation → ONLINE (recovery)
- **Latency spike** (recent avg > 3× baseline) → DEGRADED

### Health Recording

Health checks are automatically recorded after each tool execution via the RuntimeExecutor. They are persisted to SQLite (`health.db`) with:
- Individual check events (success/failure, latency, errors)
- Periodic full-record snapshots
- Time-series performance trends

### Auto-Healing

When an agent goes DEGRADED or OFFLINE:
1. The **health sweeper** (60-second interval) detects the degraded agent
2. Finds a healthy replacement from candidates matching the same tools
3. Routes future requests to the healthy agent
4. Emits `agent_auto_healed` event

During live execution, if a step targets a DEGRADED/OFFLINE agent:
1. The executor detects unhealthy status
2. Finds a healthy candidate via the agent pool
3. Re-routes the step to the healthy agent
4. The original agent's health continues to be monitored

```http
# View agent health
GET /agents/agent_shell/health

# Manual status override
POST /agents/agent_shell/health/status
Content-Type: application/json
{ "status": "ONLINE" }

# Trigger auto-heal
POST /agents/agent_shell/auto-heal

# Health check history
GET /agents/agent_shell/health/history

# Performance trends over time
GET /agents/agent_shell/health/trends
```

### Demo Scenario: Agent Recovery

1. `agent_shell` starts ONLINE
2. Network issues cause 3 consecutive tool failures
3. Status changes to DEGRADED → `agent_health_changed` event
4. 3 more failures → status changes to OFFLINE
5. Auto-healing sweeper finds `agent_backup_shell` as replacement
6. Traffic routes to backup agent
7. Original agent's health continues being checked
8. Eventually succeeds 3 times → recovers to ONLINE

---

## 11. Broadcast Queries & Aggregation

### Broadcast Queries

Send a question to multiple agents simultaneously and collect their responses.

```http
POST /broadcast-queries
Content-Type: application/json

{
  "from_agent": "agent_system",
  "question": "What is your current load?",
  "target_agents": ["agent_filesystem", "agent_git", "agent_shell"]
}
```

With timeout:
```http
POST /broadcast-queries/with-timeout
Content-Type: application/json

{
  "from_agent": "agent_system",
  "question": "Are you ready for deployment?",
  "target_agents": ["agent_filesystem", "agent_git"],
  "timeout_ms": 5000
}
```

### Query Lifecycle

```
PENDING → COLLECTING (first response) → COMPLETED (all responded or manually closed)
                                      → EXPIRED (timeout elapsed)
```

### Response Aggregation

After collecting responses, aggregate them with a strategy:

```http
POST /broadcast-queries/{query_id}/aggregate
Content-Type: application/json
{ "strategy": "MAJORITY" }
```

| Strategy | Behavior |
|----------|----------|
| **ALL** | Returns the complete dict of all responses |
| **FIRST** | Returns only the first response received |
| **MERGE** | Merges all response dicts into one |
| **MAJORITY** | Returns the most common response value |

### Timeout Auto-Sweep

A background task (30-second interval) automatically expires overdue broadcast queries.

---

## 12. Collaboration Sessions

Collaboration sessions provide a shared context space where multiple agents work together on a task.

### Session Lifecycle

1. **Create** a session linked to a task
2. Agents **join** the session
3. Agents **set context** key-value pairs (shared state)
4. Agents can **read context** set by other participants
5. Agents **leave** or session is **closed**

```http
# Create session
POST /collaborations
Content-Type: application/json

{
  "task_id": "task_abc",
  "participants": ["agent_filesystem"]
}

# Another agent joins
POST /collaborations/{session_id}/join
Content-Type: application/json
{ "agent_id": "agent_git" }

# Share context
POST /collaborations/{session_id}/context
Content-Type: application/json
{ "key": "scan_results", "value": { "files_found": 42, "issues": 3 } }

# Close when done
POST /collaborations/{session_id}/close
```

### Demo Scenario: Collaborative Code Review

1. `agent_filesystem` creates a collaboration session for task "code-review"
2. `agent_git` joins the session
3. `agent_filesystem` scans files, sets context: `{ "files": [...], "large_files": [...] }`
4. `agent_git` reads the context, runs `git.log` for those files
5. `agent_git` sets context: `{ "recent_changes": [...], "contributors": [...] }`
6. Both agents' findings are available in the shared context
7. Session is closed with combined results

---

## 13. Agent Request/Response Protocol

Direct agent-to-agent communication with request/response semantics.

### Request Lifecycle

```
PENDING → DELIVERED → RESPONDED
                   → TIMEOUT
                   → FAILED
```

```http
# Send request
POST /agent-requests
Content-Type: application/json

{
  "from_agent": "agent_filesystem",
  "to_agent": "agent_git",
  "action": "check_file_history",
  "payload": { "file": "src/main.py" }
}

# Target agent responds
POST /agent-requests/{request_id}/respond
Content-Type: application/json

{
  "from_agent": "agent_git",
  "success": true,
  "payload": { "commits": 15, "last_author": "developer@example.com" }
}
```

---

## 14. Agent Task Queue

Priority-based task queue for asynchronous agent work.

### Task Priority

| Priority | Meaning |
|----------|---------|
| 1 | Highest — process first |
| 2 | High |
| 3 | Normal (default) |
| 4 | Low |
| 5 | Lowest |

### Queue Operations

```http
# Enqueue a task
POST /agent-tasks
Content-Type: application/json

{
  "agent_id": "agent_filesystem",
  "tool": "filesystem.grep",
  "arguments": { "pattern": "TODO", "path": "." },
  "priority": 2
}

# Dequeue next task for agent (highest priority first)
POST /agent-tasks/dequeue/agent_filesystem

# Auto-execute a single task (dequeue + invoke + complete/fail)
POST /agent-tasks/{item_id}/auto-execute

# Auto-execute all queued tasks for an agent
POST /agent-tasks/auto-execute-queue/agent_filesystem
```

### Smart Task Scheduling

Let the system choose the best agent:

```http
POST /tasks/schedule
Content-Type: application/json

{
  "tool": "filesystem.grep",
  "arguments": { "pattern": "TODO", "path": "." },
  "priority": 2
}
```

Response:
```json
{
  "status": "scheduled",
  "agent_id": "agent_filesystem",
  "item_id": "atq_abc123",
  "confidence": 0.95
}
```

---

## 15. Capability Discovery & Performance

### Capability Discovery

Automatically discovers what tools each agent can handle by:
1. **Filter-based**: Expands `tool_filter` globs against the tool registry
2. **History-based**: Checks execution history from agent memory

```http
GET /agents/agent_filesystem/capabilities/discovered
```
Response:
```json
[
  { "agent_id": "agent_filesystem", "tool": "filesystem.list", "source": "filter", "confidence": 1.0 },
  { "agent_id": "agent_filesystem", "tool": "filesystem.grep", "source": "history", "confidence": 0.88 }
]
```

A background discovery sweep runs every 90 seconds. You can also trigger it manually:
```http
POST /discovery/run
```

### Performance Dashboard

Combined view of an agent's health, reputation, capabilities, and trends:

```http
GET /agents/agent_filesystem/performance
```

Compare all agents:
```http
GET /agents/performance/comparison
```

---

## 16. Agent Memory Scoping

Each agent has isolated, namespaced memory that other agents cannot access.

```http
# Set a memory key
PUT /agents/agent_filesystem/memory
Content-Type: application/json
{ "key": "last_scan_path", "value": "/home/user/projects" }

# Get all memory keys
GET /agents/agent_filesystem/memory

# Delete a specific key
DELETE /agents/agent_filesystem/memory/last_scan_path

# Clear all memory for an agent
DELETE /agents/agent_filesystem/memory
```

Memory is stored using the `agent_id:key` pattern in the global MemoryStore, ensuring complete isolation between agents.

---

## 17. Agent Communications Dashboard

The Communications Dashboard provides a unified view of all inter-agent communication across every protocol (requests, negotiations, handoffs, broadcasts, collaborations). It is the 6th sub-tab in the Agents view.

### Communications Feed

A unified timeline of all inter-agent events, newest first:

```http
GET /agents/communications/feed?limit=50
```

Returns events from all communication channels merged chronologically:
```json
[
  {
    "type": "request",
    "id": "areq_abc123",
    "from_agent": "agent_filesystem",
    "to_agent": "agent_git",
    "action": "check_file_history",
    "status": "RESPONDED",
    "timestamp": "2025-01-15T10:30:00Z"
  },
  {
    "type": "negotiation",
    "id": "neg_def456",
    "initiator": "agent_shell",
    "responder": "agent_filesystem",
    "tool": "shell.run_safe",
    "phase": "RESOLVED",
    "timestamp": "2025-01-15T10:28:00Z"
  }
]
```

The UI includes a **type filter dropdown** to show only specific event types (requests, negotiations, handoffs, broadcasts, collaborations).

### Communication Graph

A visual graph showing agents as nodes and their messages as directed edges:

```http
GET /agents/communications/graph
```

Returns:
```json
{
  "nodes": [
    { "id": "agent_filesystem", "name": "Filesystem Agent" },
    { "id": "agent_git", "name": "Git Agent" }
  ],
  "edges": [
    { "from": "agent_filesystem", "to": "agent_git", "type": "request", "count": 3 },
    { "from": "agent_shell", "to": "agent_filesystem", "type": "negotiation", "count": 1 }
  ]
}
```

In the UI, the graph is rendered as an SVG with:
- **Circular layout** — agents arranged evenly around a circle
- **Color-coded directed edges** — cyan=request, sky=response, amber=negotiation, purple=handoff, emerald=broadcast
- **Edge aggregation** — multiple messages between the same pair show a `×N` count pill at the midpoint
- **Arrowhead markers** — arrows show message direction
- **Traffic pill** — a small indigo pill below each agent's node label shows total message count (`N msgs`)
- **Interactive zoom/pan** — scroll wheel to zoom (0.25×–3×), drag to pan; shared between inline and overlay modes
- **Fullscreen overlay** — the Expand button (⤢) opens the graph in a `96vw × 90vh` glassmorphic modal for detailed exploration; ESC or click-outside to close
- **Hover tooltips** — hovering over an edge or its pill shows structured detail: `source → target | N messages | type: count`; hovering over a node shows agent ID and total traffic

### Stats Cards

The dashboard shows 4 summary cards:
- **Messages** — total agent requests + responses
- **Negotiations** — total active + resolved negotiations
- **Pending Requests** — requests still awaiting response
- **Collaborations** — active collaboration sessions

### Demo Scenario: Communication Overview

1. Create a few agent requests, start a negotiation, and a broadcast query
2. Open the **Communications** sub-tab in Agents view
3. Stats cards reflect the total counts
4. Communication graph shows agents as nodes with colored edges
5. Activity feed shows all events in reverse chronological order
6. Use the type filter to show only negotiations
7. Select a negotiation in the timeline viewer to see round-by-round history

### Message Threading

Agent messages can be grouped into conversation threads by `correlation_id`. The Agent Message Log offers a **Flat/Threads** toggle to switch between views.

```http
GET /agent-messages/threads?limit=30
```

Returns threads grouped by `correlation_id`:
```json
[
  {
    "thread_id": "t_abc123",
    "correlation_id": "corr_xyz",
    "messages": [{"source_agent": "agent_filesystem", "message_type": "delegation_request", ...}],
    "message_count": 4,
    "participants": ["agent_filesystem", "agent_git"],
    "types": ["delegation_request", "delegation_response"],
    "first_ts": "2025-01-15T10:28:00Z",
    "last_ts": "2025-01-15T10:30:00Z"
  }
]
```

**UI features:**
- **Flat view** — chronological message list; threaded messages show a purple \ud83d\udd17 `correlation_id` link
- **Threads view** — collapsible thread cards with correlation_id header, message count badge, participant list, expand/collapse
- Solo messages (no `correlation_id`) are grouped individually

---

## 18. Pipeline Lane View

The Pipeline Lane View provides a horizontal lane-based visualization of workflow chains, grouping steps by their assigned agent. Steps can be reassigned between agents via drag-and-drop.

### How It Works

1. **Select a chain** from the dropdown selector
2. Steps are grouped into horizontal **agent lanes** — one lane per agent
3. Each step is displayed as a draggable badge showing the tool name, with output_key/input_from/condition indicators
4. **Drag a step** from one agent lane to another to reassign it
5. The reassignment is persisted immediately via `PUT /workflow-chains/{id}` with a version increment

### Visual Layout

```
┌─ agent_filesystem ──────────────────────────────────┐
│  [filesystem.tree]  [filesystem.grep]               │
│    output: structure   output: todos                │
└─────────────────────────────────────────────────────┘

┌─ agent_git ─────────────────────────────────────────┐
│  [git.status]  [git.log]                            │
│    output: git_state   input: structure             │
└─────────────────────────────────────────────────────┘

┌─ agent_system ──────────────────────────────────────┐
│  [system.info]                                      │
└─────────────────────────────────────────────────────┘
```

### Cross-Agent Reassignment

Drag a step badge between lanes to reassign:
- Visual ring feedback during drag
- Optimistic UI update — the step moves immediately in the UI
- API persistence — `PUT /workflow-chains/{id}` saves the new agent assignment with version increment

### Negotiate All

The **Negotiate All** button runs pipeline negotiation across all workflow chains at once:

```http
POST /workflow-chains/negotiate-all
```

This returns assignments and any conflicts (tied agents) per chain. The UI shows a toast notification with the total conflict count.

### Conflict Resolution

When pipeline negotiation detects tied agents for a step (multiple agents with identical confidence), the UI shows an interactive **Conflict Picker** with radio buttons for each tied agent per step.

```http
POST /workflow-chains/{id}/resolve-conflicts
```

Payload:
```json
{
  "resolutions": [
    { "step_index": 0, "agent_id": "agent_filesystem" },
    { "step_index": 2, "agent_id": "agent_shell" }
  ]
}
```

Returns:
```json
{
  "chain_id": "wc_abc123",
  "applied": 2,
  "total": 3
}
```

**How it works:**
1. Run pipeline negotiation (`POST /workflow-chains/{id}/negotiate`)
2. If conflicts exist, the UI renders radio buttons for each tied agent per conflict step
3. User selects preferred agents and clicks **Resolve Conflicts**
4. Resolution applies the chosen agents to the chain steps and increments the chain version
5. Out-of-range step indices are silently ignored

### Lane Builder — Visual Pipeline Construction

The **New from Lanes** button in the Pipeline Lane View opens a visual pipeline construction mode for building chains from scratch.

**UI components:**
- **Tool Palette** — draggable list of all registered tools with a filter input
- **Agent Lanes** — horizontal lanes, each with an agent selector dropdown
- **Drop Zones** — drag tools from the palette into agent lanes to create steps
- **Add Agent Lane** button — creates new lanes dynamically

**Workflow:**
1. Click **New from Lanes** in Pipeline Lane View
2. Filter and drag tools from the palette into agent lanes
3. Add more lanes with "Add Agent Lane" and select agents
4. Fill chain name and description
5. Click **Create Chain** → POST /workflow-chains with steps assembled from lane contents

Each lane step gets the agent_id from its lane's selector and the tool from the dragged tool name.

---

## 19. Agent Blueprint Templates

Agent blueprint templates provide pre-configured agent definitions for common roles.

### Available Templates (36)

| Template ID | Name | Capabilities | Tool Filter |
|-------------|------|-------------|-------------|
| **code-reviewer** | Code Reviewer | code analysis, review | `filesystem.read_file`, `filesystem.list`, `filesystem.tree`, `filesystem.grep`, `git.status`, `git.diff`, `git.log` |
| **devops** | DevOps Agent | system health, deployment | `system.*`, `git.*`, `shell.run_safe` |
| **project-navigator** | Project Navigator | exploration, discovery | `filesystem.list`, `filesystem.tree`, `filesystem.search`, `filesystem.read_file`, `filesystem.grep` |
| **security-auditor** | Security Auditor | security scanning | `filesystem.grep`, `filesystem.tree`, `filesystem.search`, `filesystem.read_file`, `git.log` |
| **release-manager** | Release Manager | release workflows | `git.*`, `filesystem.read_file`, `filesystem.grep`, `system.info` |
| **test-engineer** | Test Engineer | test analysis | `filesystem.list`, `filesystem.tree`, `filesystem.search`, `filesystem.read_file`, `filesystem.grep` |
| **documentation-writer** | Documentation Writer | docs generation | `filesystem.read_file`, `filesystem.list`, `filesystem.tree`, `filesystem.write_file`, `filesystem.grep` |
| **ci-cd-specialist** | CI/CD Specialist | pipeline inspection | `filesystem.read_file`, `filesystem.list`, `filesystem.search`, `filesystem.grep`, `shell.run_safe` |
| **performance-analyst** | Performance Analyst | system monitoring, performance analysis | `system.*`, `process.*`, `filesystem.list`, `filesystem.grep` |
| **dependency-manager** | Dependency Manager | dependency management, package auditing | `filesystem.read_file`, `filesystem.search`, `filesystem.grep`, `git.log` |
| **infrastructure-scanner** | Infrastructure Scanner | docker/kubernetes/terraform scanning | `filesystem.read_file`, `filesystem.list`, `filesystem.search`, `filesystem.grep` |
| **onboarding-guide** | Onboarding Guide | navigation, setup assistance | `filesystem.list`, `filesystem.tree`, `filesystem.read_file`, `filesystem.search` |
| **debugger** | Debugger Agent | error investigation, debugging | `filesystem.grep`, `filesystem.read_file`, `git.log`, `git.diff`, `system.info` |
| **refactorer** | Refactorer Agent | code refactoring, pattern analysis | `filesystem.read_file`, `filesystem.list`, `filesystem.grep`, `filesystem.write_file`, `git.diff` |
| **api-designer** | API Designer | API design review, schema analysis | `filesystem.read_file`, `filesystem.grep`, `filesystem.search`, `git.log` |
| **docker-engineer** | Docker Engineer | container review, Dockerfile analysis | `filesystem.read_file`, `filesystem.search`, `filesystem.grep`, `shell.run_safe` |
| **db-optimizer** | Database Optimizer | database analysis, schema review | `filesystem.read_file`, `filesystem.grep`, `filesystem.search`, `git.log` |
| **frontend-analyst** | Frontend Analyst | HTML/CSS/JS analysis (read-only) | `filesystem.read_file`, `filesystem.list`, `filesystem.tree`, `filesystem.grep`, `filesystem.search` |
| **sre-agent** | SRE Agent | system monitoring, reliability engineering | `system.*`, `process.*`, `filesystem.grep` |
| **changelog-writer** | Changelog Writer | git history → CHANGELOG generation | `git.log`, `git.tag`, `filesystem.read_file`, `filesystem.write_file` |
| **data-engineer** | Data Engineer | data pipeline, ETL analysis | `filesystem.read_file`, `filesystem.grep`, `filesystem.search`, `filesystem.list` |

#### Coworking & Productivity

| Template ID | Name | Capabilities | Tool Filter |
|-------------|------|-------------|-------------|
| **note-taker** | Note Taker | note capture, knowledge logging | `notes.*`, `text.*`, `time.*`, `clipboard.read` |
| **personal-assistant** | Personal Assistant | coworking, reminders, snippets | `notes.*`, `clipboard.*`, `time.*`, `text.*`, `random.*`, `calc.eval` |
| **research-helper** | Research Helper | web content capture, text extraction | `notes.create`, `notes.search`, `text.*`, `clipboard.read` |
| **meeting-prep** | Meeting Prep | meeting briefs, agenda drafting | `notes.*`, `time.*`, `text.*`, `filesystem.read_file`, `filesystem.grep` |
| **daily-brief** | Daily Brief | morning briefing, day planning | `notes.*`, `time.*`, `git.status`, `git.log`, `system.info` |
| **knowledge-curator** | Knowledge Curator | note-graph maintenance, search | `notes.*`, `text.*`, `filesystem.grep` |

#### Composition Orchestrators

These agents are designed to drive **composite chains** (chains that reference other chain templates) end-to-end. They pair naturally with the `master-audit`, `release-master`, `ops-orchestration`, and `client-onboarding-pack` templates.

| Template ID | Name | Capabilities | Tool Filter |
|-------------|------|-------------|-------------|
| **audit-orchestrator** | Audit Orchestrator | security + dependency + quality audit orchestration | `filesystem.grep`, `filesystem.read_file`, `git.log`, `notes.create` |
| **release-orchestrator** | Release Orchestrator | release readiness + changelog + git hygiene orchestration | `git.*`, `filesystem.read_file`, `filesystem.grep`, `notes.create` |
| **ops-orchestrator** | Ops Orchestrator | deploy check + perf profile + log investigation orchestration | `system.*`, `process.*`, `git.status`, `git.log`, `notes.create` |

### API

```bash
# List all agent blueprint templates
GET /agent-templates

# Create agent from template
POST /agents/from-template/{template_id}
```

### UI

In the **Agents** view, click **From Template** to open the template picker. Each template shows:
- Name and description
- Capabilities (badge list)
- Tool filter (badge list)

One-click creates the agent with all fields pre-filled.

---

## 20. Workflow Studio (Visual Editor)

The **Workflow Studio** is a visual node-based workflow composer (14th UI view, Ctrl+6).

### Layout

Three-panel layout:
- **Left**: Node palette with three tabs — Tools (grouped by category), Agents (with tool count), Templates (chain + DSL)
- **Center**: SVG canvas with grid background, HTML-rendered nodes, SVG edges with cubic Bezier curves
- **Right**: Properties panel for the selected node

### Canvas Operations

| Operation | How |
|-----------|-----|
| Add node from palette | Drag tool/agent/template onto canvas |
| Add empty node | Double-click empty canvas area |
| Select node | Click node (highlights with ring) |
| Move node | Drag node body |
| Delete node | Select + press Delete key |
| Draw edge | Click output port → drag to input port |
| Clear all | Click Clear button |
| Zoom in/out | Mouse wheel (zooms towards cursor), or zoom buttons |
| Fit all nodes | Click Fit View button (auto-fits with padding) |
| Pan canvas | Toggle pan mode, or middle-mouse drag, or shift+drag |
| Toggle layout | Click `swap_horiz`/`swap_vert` button to flip between horizontal (default) and vertical flow |

### Layout Direction

The canvas defaults to **horizontal flow** (`_studio.layoutMode = 'horizontal'`):
- **Horizontal** — input port on the left edge, output port(s) on the right edge; chains flow left→right; auto-loaded chains placed at `x = 80 + i*280, y = 120`
- **Vertical** — input port on top, output port(s) on bottom; chains flow top→bottom

Toggle via the toolbar button (icon switches between `swap_horiz` and `swap_vert`). `studioRelayoutNodes()` repositions nodes along the active primary axis. Port positions, Bezier control points, and topo-sort tie-breaking all adapt to the active layout.

### Conditional Diamonds

Nodes whose tool name starts with `condition.` (or which carry a `condition` field) render as **conditional diamonds**:
- **Amber border ring** + `IF` corner badge
- **Three output ports** instead of one:
  - **TRUE** (green) — branch taken when condition evaluates true
  - **FALSE** (amber) — branch taken when condition evaluates false
  - **BRANCH** (violet) — auto-sets `branch_to` on the source step for cross-agent re-routing

Edges carry a `kind` field (`true` / `false` / `branch`) and render with matching SVG arrow markers (`stArrowTrue`, `stArrowFalse`, `stArrowBranch`) and stroke colours.

### Zoom & Pan

The canvas supports CSS transform-based zoom and pan for working with large pipelines:

**Zoom controls** (top-right overlay):
- **Zoom In / Zoom Out** buttons — step zoom in 8% increments
- **Percentage label** — shows current zoom level (15%–200%)
- **Fit View** — auto-calculates bounding box of all nodes and fits them within the viewport with 30px padding; auto-triggers on chain load when 5+ nodes are present
- **Pan toggle** (hand icon) — activates pan mode; cursor changes to grab/grabbing

**Mouse controls:**
- **Mouse wheel** — zoom towards cursor position
- **Middle-mouse drag** — pan the canvas
- **Shift + drag** — pan the canvas (alternative)
- **Pan mode + drag** — pan the canvas (when toggle is active)

All interactions (drop, double-click, node drag, edge drawing) use `studioScreenToCanvas()` to convert screen coordinates to canvas-space, ensuring correct behaviour at any zoom level and pan offset. Clearing the canvas resets zoom and pan to defaults.

### Node Properties

When a node is selected, the properties panel shows:
- **Tool** — dropdown of all registered tools (description shown below dropdown for quick reference)
- **Agent** — dropdown of all agents
- **Description** — free text
- **Arguments** — smart argument builder with dynamic typed form fields per tool (text, number, checkbox, dropdown) instead of raw JSON; JSON/Form toggle for advanced editing; `_TOOL_ARG_SCHEMAS` covers 30+ tools
- **Data Flow** section:
  - **Output Key** — string identifier for output bridging
  - **Input From** — references another step's output_key; clickable suggestions show available output keys from other nodes
- **Advanced Options** (collapsible):
  - **Condition** — `output_key:field op value` expression
  - **Branch To** — agent_id for conditional rerouting
  - **Parallel Group** — group key for concurrent execution
  - **Continue on Failure** — checkbox; when enabled the chain proceeds past this step on FAILED status instead of aborting (renders as `⏭ continue` badge on the canvas node)
- **Tooltip icons** (ℹ️) — every property field has an info icon with contextual help text
- **Inline help** — collapsible "?" help guide with 5 sections: Getting Started, Data Flow, Arguments, Advanced Features, Keyboard Shortcuts

### Edge Drawing

Edges connect output ports (right side of node) to input ports (left side of next node):
- Cubic Bezier SVG paths
- Temporary dashed line during drag
- Auto-sets `input_from` when source has `output_key`
- Prevents duplicate and self-loop connections

### Palette Tooltips

Hovering over a tool in the palette shows a rich tooltip (body-appended, viewport-clamped):
- Tool name and description
- Risk level badge (HIGH red, MED amber)
- Parameter list with required indicators
- Tooltip repositions to avoid clipping at viewport edges

### Template Loading

Click a template in the palette's Templates tab to load it into the canvas:
- Chain templates (35 available) create sequential nodes with auto-connected edges
- Workflow DSL templates (24 available) are converted to nodes similarly
- Search filter input to narrow template list; scrollable list with `max-h-80`

### Serialization

The visual graph is serialized to ordered AgentWorkflowStep format using **topological sort (Kahn's algorithm)**:
- Directed edges define dependencies
- Nodes with no incoming edges are processed first
- Result is a valid execution order for the workflow chain

### Operations

| Button | Action |
|--------|--------|
| **Save** | POST /workflow-chains → saves as workflow chain |
| **Execute** | Save + POST /workflow-chains/{id}/execute |
| **Debug** | Save + creates server-side debug session via POST /debug-sessions; stepping toolbar (Step Over, Continue, Stop) with live canvas visuals |
| **Open** | Load existing chain from glassmorphic picker modal |
| **Auto-Assign** | Save + POST /auto-assign → agents assigned to nodes |
| **Optimize** | Save + POST /apply-optimization → parallel groups added |
| **Clear** | Remove all nodes and edges |

### Open Chain

Load an existing workflow chain into the Studio canvas:
- Click **Open** in the toolbar
- Glassmorphic picker modal shows all saved chains with step counts and agent names
- Select a chain to load it into the visual editor via `studioEditChain()`

### Debug Execution (Stepping Debugger)

Interactive step-by-step debugging with real-time visual feedback on the canvas:

**Starting a debug session:**
- Click **Debug** in the toolbar
- Chain is saved, then a server-side debug session is created via `POST /debug-sessions`
- A debug toolbar appears with **Step Over**, **Continue**, and **Stop** buttons
- A step counter shows progress (e.g. "2 / 5")
- All pending steps appear in the results tray upfront

**Stepping controls:**
- **Step Over** — executes the next step only, then pauses (`POST /debug-sessions/{id}/step`)
- **Continue** — runs all remaining steps to completion (`POST /debug-sessions/{id}/continue`)
- **Stop** — aborts the session and cleans up (`DELETE /debug-sessions/{id}`)
- Buttons are disabled while a step is executing

**Canvas visuals** — each node shows its current state:
- **Amber pulsing border + spinner** — step is running
- **Green glow + ✓ badge** — step succeeded
- **Red glow + ✗ badge** — step failed
- **Gray dimmed + ⊘ badge** — step skipped (condition unmet)

**Resizable results tray:**
- Drag handle at the top edge of the tray for vertical resize (min 80px, max 80vh)
- Results fill incrementally with per-step output and duration metrics
- Auto-scrolls to the current step
- Execution stops on first failure

**Debug Sessions API:**

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/debug-sessions` | Create session from chain_id; returns session_id, total_steps, step list |
| POST | `/debug-sessions/{id}/step` | Execute next step; returns {done, index, tool, status, duration_ms, output} |
| POST | `/debug-sessions/{id}/continue` | Run all remaining steps; returns list of results |
| DELETE | `/debug-sessions/{id}` | Clean up session |

### Bidirectional Editing

Existing workflow chains can be loaded into the Studio:
- Click **Studio** button on any workflow chain card
- Chain steps are converted to positioned nodes with edges
- Edit visually, then save back to the same chain

---

## 21. Demo Storyboard — Multi-Agent Scenarios

### Scenario 1: "Full Project Analysis" (5 minutes)

**Goal**: Show agents collaborating to analyze a codebase.

**Steps**:

1. **Create a Workflow Chain** — "Project Analysis Pipeline"
   - Step 1: `agent_filesystem` → `filesystem.tree` (output_key: "structure")
   - Step 2: `agent_git` → `git.status` (output_key: "git_state", parallel_group: "scan")
   - Step 3: `agent_filesystem` → `filesystem.grep` with pattern "TODO|FIXME" (output_key: "todos", parallel_group: "scan")
   - Step 4: `agent_system` → `system.info` (output_key: "env")
   - Step 5: `agent_filesystem` → `filesystem.read_file` with path "README.md" (condition: `structure:files not_empty`)

2. **Auto-Assign Agents** — System selects best agent for each step

3. **Execute with Parallel Groups** — Steps 2-3 run concurrently

4. **View Execution History** — Check ✓/✗/⊘ per step

5. **Replay** — Re-run with different arguments

**What to observe**:
- Parallel execution of independent steps
- Conditional gating on Step 5
- Capability scores updated after execution
- Execution record with timing data

---

### Scenario 2: "Consensus-Driven Deployment" (3 minutes)

**Goal**: Show multi-agent voting before a critical operation.

**Steps**:

1. **Set orchestration strategy** to CAPABILITY_SCORE
2. **Create consensus request**: "Should we run the deployment script?"
   - Candidates: `agent_filesystem`, `agent_git`, `agent_shell`
   - Strategy: MAJORITY
3. **Vote as each agent**:
   - `agent_filesystem`: APPROVE (weight 0.8, reason: "Config files validated")
   - `agent_git`: APPROVE (weight 0.7, reason: "No uncommitted changes")
   - `agent_shell`: REJECT (weight 0.4, reason: "High system load")
4. **Resolve** — Majority approves (weighted 1.5 vs 0.4)
5. **Check consensus patterns** — Tool approval rate tracked

**What to observe**:
- Weighted voting in action
- Vote reasons provide audit trail
- Pattern learning accrues over time

---

### Scenario 3: "Agent Negotiation & Recovery" (4 minutes)

**Goal**: Show agents negotiating tool ownership and health-based recovery.

**Steps**:

1. **Start negotiation**: `agent_filesystem` vs `agent_shell` for `shell.run_safe`
   - Initiator: `agent_filesystem` (priority: HIGH)
   - Responder: `agent_shell` (priority: NORMAL)
2. **Counter-propose**: `agent_shell` counters with itself
3. **Auto-resolve by priority** — `agent_filesystem` wins (HIGH < NORMAL)
4. **Simulate agent failure**:
   - Set `agent_filesystem` health to OFFLINE manually
5. **Trigger auto-heal** — System finds replacement
6. **Task handoff**: `agent_filesystem` → `agent_shell` with reason
7. **Accept and complete** the handoff

**What to observe**:
- Multi-round negotiation with priorities
- Health state transitions (ONLINE → OFFLINE)
- Automatic rerouting on failure
- Handoff lifecycle with accept/complete

---

### Scenario 4: "Broadcast Intelligence Gathering" (2 minutes)

**Goal**: Show agents collectively answering a question.

**Steps**:

1. **Broadcast query**: "What capabilities do you have for Python analysis?"
   - Targets: all 4 built-in agents
   - Timeout: 10000ms
2. **Respond as each agent** with relevant capabilities
3. **Aggregate responses** using MERGE strategy
4. **Create collaboration session** based on findings
5. Agents **join** and **share context**

**What to observe**:
- Parallel query to multiple agents
- Response aggregation strategies
- Collaboration session with shared state
- Timeout handling

---

### Scenario 5: "Smart Task Scheduling & Queue Processing" (3 minutes)

**Goal**: Show intelligent task routing and batch processing.

**Steps**:

1. **Schedule a task**: `filesystem.grep` with pattern "import" — system auto-selects best agent
2. **Enqueue multiple tasks** with different priorities:
   - Priority 1: `filesystem.tree` (critical)
   - Priority 3: `filesystem.grep` (normal)
   - Priority 5: `system.info` (low)
3. **Auto-execute agent queue** — Tasks drain in priority order
4. **View capability scores** updated after execution
5. **Check reputation** — Cross-task metrics

**What to observe**:
- Agent auto-selection based on capability confidence
- Priority ordering in queue processing
- Capability scores increasing with successful execution
- Reputation score reflecting overall agent reliability

---

### Quick Reference: UI Navigation

| Panel | Location | Key Features |
|-------|----------|-------------|
| Agent CRUD | Agents view (top) | Create/edit/delete agents, tool filter editing |
| Orchestration | Agents view | Strategy selector, fallback attempts |
| Delegation Chains | Agents view | Active chains with depth indicators |
| Consensus | Agents view | Vote buttons, resolve, pattern learning |
| Negotiations | Agents view | Counter/accept/reject, auto-counter, priority badges |
| Handoffs | Agents view | Accept/decline/complete lifecycle |
| Agent Health | Agents view | Green/amber/red indicators, auto-heal |
| Capability Learning | Agents view | Per-tool confidence scores |
| Agent Reputation | Agents view | Cross-task reputation score |
| Workflow Chains | Agents view | Step editor, execute, parallel, templates |
| Chain Execution History | Agents view | ✓✗⊘ step counts, replay |
| Broadcast Queries | Agents view | Query/respond/aggregate |
| Collaboration Sessions | Agents view | Join/leave, shared context |
| Agent Requests | Agents view | Request/respond protocol |
| Agent Task Queue | Agents view | Enqueue/dequeue, auto-execute |
| Capability Discovery | Agents view | Filter/history source badges |
| Performance Dashboard | Agents view | Comparison metrics, trend charts |
| Agent Memory | Agents view | Per-agent key-value store |
| Performance Trends | Agents view | SVG time-series charts |
| Health History | Agents view | Check logs, latency tracking |
| Communications Dashboard | Agents view (6th sub-tab) | Stats cards, SVG graph, activity feed, type filter |
| Negotiation Timeline | Agents view (Communications) | Phase-colored round-by-round history |
| Pipeline Lane View | Agents view (Pipelines) | Agent lanes, drag-and-drop reassignment, Negotiate All, Conflict Picker, Lane Builder |
| Workflow Studio | Studio view (Ctrl+6) | Visual node editor, SVG canvas, smart arg builder, bidirectional chain editing, template loading |
| Security Center | Security view | Secrets Vault (AES-256-GCM), Audit Log, Vulnerability Scanner, Credential Scrubber |
| MCP Protocol | MCP view | Server Registry, Discovered Tools, stdio transport |
| Context Directory | Chat bar (context pill) | Active project directory, git repo scanner, session persistence |

---

## 22. New Tools (Sprint 58)

Five new tools were added to expand agent capabilities.

### filesystem.copy

Copy a file or directory tree to a new location.

```json
{
  "source": "src/module.py",
  "destination": "backup/module.py",
  "overwrite": false
}
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `source` | string | ✓ | Source path (file or directory) |
| `destination` | string | ✓ | Destination path |
| `overwrite` | bool | — | Allow overwriting existing files (default: false) |

Risk level: **MEDIUM**. Workspace-bounded. Returns `{ "copied": true, "source": "...", "destination": "..." }`.

### filesystem.mkdir

Create a directory tree (equivalent to `mkdir -p`).

```json
{ "path": "src/new/nested/dir" }
```

Risk level: **LOW**. Workspace-bounded. Returns `{ "created": true, "path": "..." }`.

### git.tag

List, create, or delete git tags.

```json
{ "action": "list" }
{ "action": "create", "name": "v1.2.0", "message": "Release v1.2.0" }
{ "action": "delete", "name": "v1.1.0" }
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | string | ✓ | `list`, `create`, or `delete` |
| `name` | string | For create/delete | Tag name |
| `message` | string | — | Annotation message for annotated tags |

Risk level: **MEDIUM**.

### git.merge

Merge a branch into the current branch.

```json
{ "branch": "feature/my-feature", "no_ff": true }
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `branch` | string | ✓ | Branch name to merge |
| `no_ff` | bool | — | Force non-fast-forward merge (default: false) |

Risk level: **HIGH**. Requires approval before execution.

### system.env

Read environment variables with automatic sensitive-key redaction.

```json
{ "key": "PATH" }   // read a single variable
{}                   // read all variables (20+ sensitive key patterns redacted)
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `key` | string | — | Specific variable name; omit to read all |

Risk level: **LOW**. Values matching patterns like `*API_KEY*`, `*PASSWORD*`, `*TOKEN*`, `*SECRET*` are automatically replaced with `[REDACTED]`.

---

## 23. GitHub Integration

Machina OS includes a dedicated GitHub connection that is independent of the LLM provider.

### Configuration

In **Settings → GitHub Connection**:
1. Enter a GitHub Personal Access Token (PAT)
2. Click **Connect**
3. The status dot turns green and shows the authenticated username

### API

```http
# Get GitHub connection status
GET /github/status

# Configure GitHub token
POST /github/config
Content-Type: application/json
{ "token": "ghp_..." }

# Test connection and validate token
GET /github/test
```

### Status Bar Indicator

The system status bar shows a GitHub connection dot (green = connected, grey = not connected) with the authenticated username.

### Use in Agents

When GitHub is connected, git agents use the PAT for authenticated operations (clone private repos, push to protected branches, etc.). The token is stored in preferences and restored on restart.

---

## 24. Security Center

The Security Center is a dedicated 15th UI view with four sub-tabs for secrets management, auditing, vulnerability scanning, and credential scrubbing.

### Secrets Vault

AES-256-GCM encrypted secret storage. Secrets are stored locally in SQLite with per-secret nonces and PBKDF2 key derivation (600k iterations). Falls back to XOR+HMAC authenticated encryption when the `cryptography` package is unavailable.

```http
POST   /security/secrets              # Store a secret
GET    /security/secrets              # List secret names (values never returned)
DELETE /security/secrets/{name}       # Delete a secret
```

### Audit Log

SOC 2-compatible immutable audit log with SHA-256 hash chains. Each entry includes the hash of the previous entry for tamper detection.

```http
GET  /security/audit                  # Query log (filters: actor, action, risk_level)
GET  /security/audit/summary          # Aggregate statistics
GET  /security/audit/verify           # Verify chain integrity
GET  /security/audit/export           # Export as JSON
```

### Vulnerability Scanner

14-pattern static analysis engine covering SQL injection, XSS, SSRF, command injection, JWT issues, hardcoded secrets, path traversal, insecure deserialization, and eval/exec.

```http
POST /security/analyze
Content-Type: application/json
{ "code": "def get_user(id): return db.execute(f'SELECT * FROM users WHERE id={id}')" }
```

Returns a list of `SecurityFinding` objects with CWE IDs and severity levels (CRITICAL/HIGH/MEDIUM/LOW/INFO).

### Credential Scrubber

20+ regex patterns for API keys (OpenAI, GitHub, GitLab, Slack, Google, AWS, Azure), JWTs, bearer tokens, private keys, and connection strings.

```http
POST /security/scrub
Content-Type: application/json
{ "text": "export OPENAI_API_KEY=sk-proj-abc123" }
```

Tool outputs are automatically scrubbed before being logged or sent to the UI. Custom patterns can be registered programmatically for project-specific secrets.

---

## 25. MCP Protocol Support

Machina OS implements the **Model Context Protocol (MCP)** to connect to external tool servers via JSON-RPC 2.0 over stdio (subprocess transport).

### How It Works

1. Register an MCP server in the registry
2. Connect — Machina spawns the subprocess and performs the initialize handshake (protocol version 2024-11-05)
3. Remote tools are discovered via `tools/list` and registered with the `mcp.<server>.<tool>` namespace
4. Any agent with `mcp.*` in its `tool_filter` can invoke remote MCP tools

### Server Registry

```http
# List registered servers
GET /mcp/servers

# Register a new server
POST /mcp/servers
Content-Type: application/json
{
  "name": "my-mcp-server",
  "transport": "stdio",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path"],
  "auto_connect": true
}

# Connect / disconnect
POST /mcp/servers/{id}/connect
POST /mcp/servers/{id}/disconnect

# Delete server
DELETE /mcp/servers/{id}

# List all discovered MCP tools
GET /mcp/tools
```

### MCP UI

The **MCP** view (16th UI view) has two sub-tabs:
- **Server Registry** — register/connect/disconnect/delete MCP servers with status indicators
- **Discovered Tools** — grid of all registered MCP tools with parameters, risk levels, and source server

### Using MCP Tools in Agents

Set an agent's `tool_filter` to include `mcp.*` to allow all MCP tools, or `mcp.my_server.*` for a specific server:

```json
{
  "name": "External Tool Agent",
  "tool_filter": ["mcp.*"],
  "capabilities": ["external_tools"]
}
```

---

## 26. Context Directory

The context directory sets the active working directory for agent filesystem and git operations. It persists across sessions and is visible in the Neural Link chat bar.

### API

```http
# Get current context directory
GET /context/dir

# Set context directory
PUT /context/dir
Content-Type: application/json
{ "path": "/home/user/my-project" }
```

### UI

A grey pill above the chat input shows the current context path. Clicking it opens the **Context Picker**:
- Displays the current path with breadcrumb navigation
- Scans parent directories for git repositories
- One-click selection of any detected git repo as the new context

### Effect on Agents

When a context directory is set, tool arguments that reference `"."` or relative paths are resolved under the context directory. Agents automatically operate within the selected project without requiring explicit path arguments in every step.

### Test Isolation

`clear_intake_state()` resets the context directory reference along with workflow store refs, preventing test contamination between sessions.

---

## 27. Neural Link UI Enhancements

### Done Panel (Collapsed by Default)

Completed plan cards collapse to a one-line summary showing:
- **COMPLETED** badge with step ratio (e.g., `3/3 steps — done`)
- **Inline result snippet** using the same `formatToolOutput` renderer as step details (git.log → amber hash pills, filesystem.list → icons, etc.)
- **⟩ steps** toggle button to expand/collapse the full step list

The collapsed view keeps the result visible without cluttering the conversation. Failed plans show how many steps failed.

### Smart Typeahead

The chat input shows a contextual suggestion dropdown as you type. Matching on 50+ trigger keywords covers all major tool categories:

| Category | Triggers |
|----------|----------|
| Git | `git`, `diff`, `commit`, `branch`, `log`, `stash`, `merge`, `tag` |
| Filesystem | `list`, `find`, `file`, `tree`, `read`, `write`, `copy`, `delete` |
| System | `system`, `disk`, `memory`, `env`, `info`, `stat` |
| Process | `process`, `stop`, `kill` |
| VS Code | `vscode`, `vs`, `code`, `ext`, `diag` |
| Security | `secu`, `vuln`, `scan` |
| General | `create`, `run`, `search`, `open`, `analyze`, `debug`, `refactor`, `help` |

**Interaction:**
- **↑/↓ arrows** — navigate suggestions without modifying input
- **Enter** — pick highlighted suggestion and send immediately (single keypress)
- **Mouse click** — pick and send immediately
- **Escape** — dismiss dropdown

### Natural-Language Git Routing

Git-related phrases are automatically detected and routed to the correct git sub-tool:

| Phrase | Routes to |
|--------|-----------|
| "show me recent commits" | `git.log` |
| "what changed recently" | `git.diff` |
| "current branch" | `git.status` |
| "show git history" | `git.log` |
| "what's different" | `git.diff` |
| "list branches" | `git.branch` |

---

## Appendix: Complete API Route Reference

### Agent CRUD
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/agents` | List all agents |
| POST | `/agents` | Create agent |
| GET | `/agents/{id}` | Get agent |
| PUT | `/agents/{id}` | Update agent |
| DELETE | `/agents/{id}` | Delete agent |
| GET | `/agents/summary` | Fleet health summary |
| GET | `/agents/{id}/messages` | Agent message history |

### Orchestration
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/orchestration` | Get strategy config |
| PUT | `/orchestration` | Update strategy |

### Consensus
| Method | Route | Description |
|--------|-------|-------------|
| POST | `/consensus` | Create request |
| GET | `/consensus` | List requests |
| GET | `/consensus/{id}` | Get request |
| POST | `/consensus/{id}/vote` | Cast vote |
| POST | `/consensus/{id}/resolve` | Resolve |
| DELETE | `/consensus/{id}` | Delete |
| GET | `/consensus/patterns` | Learned patterns |
| GET | `/consensus/patterns/{tool}` | Pattern for tool |

### Negotiations
| Method | Route | Description |
|--------|-------|-------------|
| POST | `/negotiations` | Start |
| GET | `/negotiations` | List |
| GET | `/negotiations/{id}` | Get |
| POST | `/negotiations/{id}/counter` | Counter-propose |
| POST | `/negotiations/{id}/accept` | Accept |
| POST | `/negotiations/{id}/reject` | Reject |
| POST | `/negotiations/{id}/resolve` | Auto-resolve |
| POST | `/negotiations/{id}/auto-counter` | Auto-counter |
| GET | `/negotiations/{id}/timeline` | Round-by-round history |

### Handoffs
| Method | Route | Description |
|--------|-------|-------------|
| POST | `/handoffs` | Request |
| GET | `/handoffs` | List |
| GET | `/handoffs/{id}` | Get |
| POST | `/handoffs/{id}/accept` | Accept |
| POST | `/handoffs/{id}/decline` | Decline |
| POST | `/handoffs/{id}/complete` | Complete |
| POST | `/handoffs/{id}/cancel` | Cancel |

### Health
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/agents/health` | All health records |
| GET | `/agents/{id}/health` | Agent health |
| POST | `/agents/{id}/health/status` | Manual override |
| GET | `/agents/{id}/health/history` | Check history |
| GET | `/agents/{id}/health/trends` | Trends |
| POST | `/agents/{id}/auto-heal` | Trigger heal |

### Workflow Chains
| Method | Route | Description |
|--------|-------|-------------|
| POST | `/workflow-chains` | Create |
| GET | `/workflow-chains` | List |
| GET | `/workflow-chains/{id}` | Get |
| DELETE | `/workflow-chains/{id}` | Delete |
| POST | `/workflow-chains/{id}/execute` | Execute |
| POST | `/workflow-chains/{id}/execute-parallel` | Parallel execute |
| PUT | `/workflow-chains/{id}` | Update (versioned) |
| POST | `/workflow-chains/{id}/rollback` | Rollback version |
| GET | `/workflow-chains/{id}/versions` | Version history |
| POST | `/workflow-chains/{id}/negotiate` | Negotiate pipeline |
| POST | `/workflow-chains/{id}/auto-assign` | Auto-assign agents |
| POST | `/workflow-chains/{id}/optimize` | Optimize parallelism |
| POST | `/workflow-chains/{id}/apply-optimization` | Apply optimization |
| GET | `/workflow-chain-templates` | List templates |
| POST | `/workflow-chains/from-template/{id}` | Create from template |
| POST | `/workflow-chains/negotiate-all` | Bulk negotiate all chains |
| POST | `/workflow-chains/{id}/resolve-conflicts` | Resolve tied agents |

### Chain Executions & Replay
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/chain-executions` | List executions |
| GET | `/chain-executions/{id}` | Get execution |
| POST | `/chain-executions/{id}/replay` | Replay |
| GET | `/chain-replays` | List replays |
| GET | `/chain-replays/{id}` | Get replay |

### Broadcasts
| Method | Route | Description |
|--------|-------|-------------|
| POST | `/broadcast-queries` | Create |
| POST | `/broadcast-queries/with-timeout` | Create with timeout |
| GET | `/broadcast-queries` | List |
| GET | `/broadcast-queries/{id}` | Get |
| POST | `/broadcast-queries/{id}/respond` | Respond |
| POST | `/broadcast-queries/{id}/complete` | Complete |
| POST | `/broadcast-queries/{id}/aggregate` | Aggregate |
| POST | `/broadcast-queries/{id}/expire` | Expire |

### Capability Announcements
| Method | Route | Description |
|--------|-------|-------------|
| POST | `/capability-announcements` | Announce |
| GET | `/capability-announcements` | List |

### Collaborations
| Method | Route | Description |
|--------|-------|-------------|
| POST | `/collaborations` | Create |
| GET | `/collaborations` | List |
| GET | `/collaborations/{id}` | Get |
| POST | `/collaborations/{id}/join` | Join |
| POST | `/collaborations/{id}/leave` | Leave |
| POST | `/collaborations/{id}/context` | Set context |
| POST | `/collaborations/{id}/close` | Close |

### Agent Requests
| Method | Route | Description |
|--------|-------|-------------|
| POST | `/agent-requests` | Send |
| GET | `/agent-requests` | List |
| GET | `/agent-requests/{id}` | Get |
| POST | `/agent-requests/{id}/respond` | Respond |

### Agent Tasks
| Method | Route | Description |
|--------|-------|-------------|
| POST | `/agent-tasks` | Enqueue |
| GET | `/agent-tasks` | List |
| GET | `/agent-tasks/{id}` | Get |
| POST | `/agent-tasks/dequeue/{agent_id}` | Dequeue next |
| POST | `/agent-tasks/{id}/complete` | Complete |
| POST | `/agent-tasks/{id}/fail` | Fail |
| POST | `/agent-tasks/{id}/cancel` | Cancel |
| POST | `/agent-tasks/{id}/auto-execute` | Auto-execute one |
| POST | `/agent-tasks/auto-execute-queue/{agent_id}` | Auto-execute all |
| POST | `/tasks/schedule` | Smart schedule |

### Capabilities & Performance
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/agents/{id}/capabilities` | Capability scores |
| GET | `/agents/{id}/capabilities/discovered` | Discovered |
| GET | `/agents/{id}/reputation` | Reputation |
| GET | `/agents/{id}/memory` | Agent memory |
| PUT | `/agents/{id}/memory` | Set memory |
| DELETE | `/agents/{id}/memory` | Clear memory |
| GET | `/agents/{id}/performance` | Full snapshot |
| GET | `/agents/performance/comparison` | Compare all |
| POST | `/discovery/run` | Run discovery |
| GET | `/discovery/status` | Discovery status |

### Communications Dashboard
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/agents/communications/feed` | Unified event feed |
| GET | `/agents/communications/graph` | Agent communication graph |
| GET | `/agent-messages/threads` | Threaded message conversations |

### Agent Templates
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/agent-templates` | List agent blueprint templates |
| POST | `/agents/from-template/{id}` | Create agent from template |

### GitHub Integration
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/github/status` | Connection status + username |
| POST | `/github/config` | Set GitHub PAT token |
| GET | `/github/test` | Test token against GitHub API |

### Security
| Method | Route | Description |
|--------|-------|-------------|
| POST | `/security/secrets` | Store encrypted secret |
| GET | `/security/secrets` | List secret names |
| DELETE | `/security/secrets/{name}` | Delete secret |
| POST | `/security/analyze` | Scan code for vulnerabilities |
| GET | `/security/audit` | Query audit log |
| GET | `/security/audit/summary` | Audit statistics |
| GET | `/security/audit/verify` | Verify hash chain |
| GET | `/security/audit/export` | Export audit log as JSON |
| POST | `/security/scrub` | Scrub credentials from text |

### MCP Protocol
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/mcp/servers` | List MCP servers |
| POST | `/mcp/servers` | Register MCP server |
| DELETE | `/mcp/servers/{id}` | Delete MCP server |
| POST | `/mcp/servers/{id}/connect` | Connect to MCP server |
| POST | `/mcp/servers/{id}/disconnect` | Disconnect from MCP server |
| GET | `/mcp/tools` | List all discovered MCP tools |

### Context Directory
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/context/dir` | Get current context directory |
| PUT | `/context/dir` | Set context directory |

### New Filesystem Tools
| Tool | Risk | Description |
|------|------|-------------|
| `filesystem.copy` | MEDIUM | Copy file or directory tree |
| `filesystem.mkdir` | LOW | Create directory tree (mkdir -p) |

### New Git Tools
| Tool | Risk | Description |
|------|------|-------------|
| `git.tag` | MEDIUM | List/create/delete git tags |
| `git.merge` | HIGH | Merge branch into current branch |

### New System Tools
| Tool | Risk | Description |
|------|------|-------------|
| `system.env` | LOW | Read environment variables (sensitive values redacted) |
