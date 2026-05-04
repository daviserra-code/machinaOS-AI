Overview

> Updated for Sprint 49 — v0.2.0, 1964 tests, 491 build items, 14 views, 40 tools.

MachinaOS is a local-first, intent-driven operating environment that transforms natural language goals into safe, inspectable, tool-executed system actions.

MachinaOS is not a chatbot attached to a dashboard.

It is an agentic runtime layer that sits above an existing operating system and coordinates:

user intent

structured plans

tool execution

approvals

event timelines

persistent context

Its architectural role is similar to an operating shell, orchestration layer, and developer cockpit combined.

1. System Identity

MachinaOS should be understood as:

an AI-native operating layer for developer-centric workflows

It does not replace the kernel.

It does not attempt to replace the host operating system in early stages.

Instead, it introduces a higher semantic layer above the host OS, where the system can reason about:

goals

tasks

projects

approvals

workspace state

execution history

In classic systems:

user -> app -> OS -> hardware

In MachinaOS:

user -> intent -> planner -> policy -> executor -> tools -> host OS

This additional semantic layer is the core innovation.

2. Architectural Goals

MachinaOS must satisfy the following goals:

2.1 Intent-Native Operation

The user should be able to express outcomes rather than manually coordinate every step.

Example:

“Open the project, check git state, inspect errors, and prepare the workspace.”

2.2 Tool-Verified Reality

The system must never claim actions occurred unless a tool confirms execution.

2.3 Human-Governed Autonomy

Automation is allowed, but dangerous actions must remain constrained by policy and approvals.

2.4 Observability

Every meaningful action must be visible through logs, events, timelines, and execution traces.

2.5 Local-First Reliability

Core orchestration should run locally and continue to function even with degraded model availability.

3. High-Level Architecture

MachinaOS is composed of the following major layers:

Presentation Layer
Neural Interface Layer
Intent & Planning Layer
Policy & Trust Layer
Execution Layer
Tool Layer
System Adapter Layer
State, Memory & Event Layer
Host Operating System

Each layer has a distinct responsibility.

4. Layer Breakdown
4.1 Presentation Layer

This is the visual operating surface of MachinaOS.

It includes:

Home Dashboard (health cards, event feed, workspace context)
Chat / Neural Link (conversational interface with streaming)
Tools Registry (40 tools with risk badges)
Memory Browser (scopes, preferences, workspaces, sessions)
Workflow Composer (DSL workflows with templates)
Workflow Studio (visual node-based editor)
Agents (fleet manager, 6 sub-tabs: Fleet, Coordination, Performance, Monitoring, Pipelines, Communications)
Timeline (task history with expand/collapse)
File Explorer (directory browser with preview)
Process Monitor (sortable table with stop controls)
Metrics Dashboard (success rate, tool performance, SVG charts)
Event Inspector (filter by type/source/severity, pagination)
Settings (LLM config, personality, preferences, RAG status)
Command Palette (Ctrl+K fuzzy search)
System Status Bar (persistent bottom bar)
Notification Center (bell badge, toast popups)

Responsibilities:

present current system state

expose active tools

show pending approvals

visualize recent actions

provide entry points into workflows

This layer should remain transparent and operational rather than decorative.

The UI exists to make the runtime inspectable.

4.2 Neural Interface Layer

The Neural Link is the conversational and command interface between the user and MachinaOS.

Responsibilities:

accept natural language input

normalize intent requests

launch workflows

surface clarifications when needed

provide concise task feedback

Examples:

“List project files”

“Set up the repo”

“Check git status”

“Resume my previous task”

This layer should not directly execute system effects.

It is an interface, not an execution engine.

4.3 Intent & Planning Layer

This layer translates user requests into structured, executable plans.

Subcomponents:

Intent Intake

Task Normalizer

Planner

Plan Validator

Responsibilities:

extract intent

detect entities and constraints

generate step-by-step plans

assign tools to actions

estimate ambiguity and risk

validate plan structure before execution

Example output:

Intent: analyze_repository
Entities: /project/path
Constraints: local_only
Plan:
  1. filesystem.list
  2. filesystem.read_file(README.md)
  3. git.status
  4. summarize_structure

This layer must remain separate from execution.

The planner proposes.
It does not act.

4.4 Policy & Trust Layer

This layer governs what MachinaOS is allowed to do.

Subcomponents:

Risk Classifier

Policy Engine

Approval Manager

Permission Resolver

Responsibilities:

classify action risk

determine allow / block / approval-needed

apply workspace-specific restrictions

prevent dangerous automation

create approval prompts with action previews

Typical protected actions:

destructive file writes

shell execution

process termination

git push

network access

credential use

This layer is the closest equivalent to a security and permission system in MachinaOS.

### 4.4.1 Security Layer

Sits alongside the Policy Engine and provides four dedicated security modules, all initialised in `MachinaCore.__init__()` and accessible via `core/security/`.

| Module | Purpose | Storage |
|--------|---------|---------|
| **EncryptionStore** | AES-256-GCM encrypted secret vault. PBKDF2 key derivation (600 000 iterations), per-secret nonces, SQLite-backed (`secrets.db`). Falls back to XOR + HMAC when `cryptography` is unavailable. | `secrets.db` |
| **AuditLog** | SOC 2-compatible immutable event ledger. Every security-sensitive action (secret access, code scan, mode change) is recorded as an `AuditEntry`. Entries are linked by a SHA-256 hash chain — each `chain_hash = SHA-256(prev_hash : audit_id : timestamp)` — so tampering with or deleting any row breaks the chain. `verify_chain()` walks entries in insertion order and reports breaks. | `audit.db` |
| **SecurityAnalyzer** | Static vulnerability scanner. Scans code line-by-line against 14 regex patterns covering SQL injection (CWE-89), command injection (CWE-78), XSS (CWE-79), SSRF (CWE-918), hardcoded secrets (CWE-798), insecure deserialization (CWE-502), path traversal (CWE-22), and dynamic eval/exec (CWE-95). Each match produces a `SecurityFinding` with CWE ID, severity, code snippet, line number, and remediation guidance. Comment lines are skipped automatically. |  — (stateless) |
| **CredentialScrubber** | Regex-based secret redaction engine with 21 built-in patterns. Detects and replaces API keys (OpenAI, Anthropic, GitHub, GitLab, Slack, Google, AWS, Azure), JWTs, Bearer/Authorization headers, PEM private keys, connection strings, and generic `password=`/`token=` values. Module-level `scrub_text()` and `scrub_output()` are wired into logs and API responses system-wide, not just the UI tool. Custom patterns and literal secrets can be registered at runtime. | — (stateless) |

The **Security Center** UI (15th view, 4 sub-tabs) exposes all four modules through dedicated panels: Secrets Vault, Audit Log, Vulnerability Scanner, and Credential Scrubber.

**Self-reinforcing audit trail:** storing, reading, or deleting a secret and scanning code all automatically record audit entries — so the audit log tracks who used the security tools and when.

4.5 Execution Layer

This layer turns approved plans into real tool invocations.

Subcomponents:

Executor

Step Runner

Retry Handler

Failure Recovery

Rollback Coordinator

Responsibilities:

execute plan steps sequentially or in controlled groups

collect tool outputs

emit execution events

handle failure states

stop on unsafe or blocked conditions

support resumable tasks

The executor is where the system touches reality.

It must be deterministic, observable, and strict.

4.6 Tool Layer

Tools are the only valid mechanism for changing system state.

Each tool must expose:

name

description

input schema

output schema

risk level

category

version

Example tool domains:

filesystem (9 tools: list, read_file, write_file, move, delete, tree, search, grep, semantic_search)
git (10 tools: status, log, diff, checkout, clone, branch, pull, push, commit, stash)
shell (2 tools: run, run_safe)
process (4 tools: list, info, start, stop)
browser (3 tools: open_url, search_files, find_recent)
vscode (7 tools: open_workspace, open_file, list_extensions, install_extension, run_task, diff, read_diagnostics)
system (4 tools: status, info, memory, disk)

Total: 40 registered tools across 7 domains.

Tool design rules:

one responsibility per tool

typed inputs and outputs

structured failure states

no hidden side effects

mandatory event emission

Think of tools as agentic system calls.

4.7 System Adapter Layer

This layer translates MachinaOS tool requests into host-OS-compatible actions.

Adapters may include:

filesystem adapters

shell adapters

Git adapters

VS Code adapters

process control adapters

browser automation adapters

OS-specific adapters for Windows / Linux / macOS

Responsibilities:

isolate platform differences

enforce execution boundaries

keep tool semantics consistent across environments

This is what lets MachinaOS stay conceptually stable while the host OS varies.

4.8 State, Memory & Event Layer

This layer provides continuity, traceability, and context.

Subcomponents:

Event Bus

Event Log

Session Store

Project Memory

User Preference Store

Task History

Snapshot Store

Responsibilities:

persist events

restore prior context

record completed tasks

maintain workspace knowledge

support resume / replay / inspect

Suggested memory classes:

Session Memory

Short-lived context for the current active interaction.

Task Memory

Execution-specific data for current and recent workflows.

Project Memory

Persistent knowledge attached to a repo or workspace.

User Preference Memory

Stable behavior preferences, defaults, and interaction norms.

Telemetry Memory

Operational data for reliability tracking and performance analysis.

This layer is the long-term nervous system of MachinaOS.

### 4.9 Agent Coordination Layer (Sprint 17-49)

This layer enables multi-agent collaboration across specialized roles.

Subcomponents:

AgentDefinition (capability profiles with tool_filter globs)
AgentPool (register, find, score, strategy-based selection)
AgentBus (pub/sub messaging, consensus, negotiation, handoffs, workflow chains)
AgentStore (SQLite persistence for user-created agents)
DelegationChain (cycle detection, depth limiting)
HealthStore (SQLite persistence for health checks, snapshots, trends)

**Inter-agent communication model:**

The AgentBus is the central nervous system of multi-agent coordination. It provides 6 distinct communication channels, each serving a different interaction pattern:

| Channel | Pattern | When It Fires |
|---------|---------|---------------|
| **Bus Messages** | Pub/sub broadcast | Every agent lifecycle event, delegation, health change |
| **Requests** | Point-to-point ask/respond | Direct agent-to-agent task requests |
| **Broadcast Queries** | One-to-many poll | Gathering information from multiple agents (with timeout + aggregation) |
| **Negotiations** | Bilateral propose/counter | Resolving tool ownership when multiple agents match a capability |
| **Handoffs** | Formal transfer | Delegating a task step from one agent to another with preconditions |
| **Collaborations** | Shared session | Multi-agent work on a common task with shared context dict |

These protocols fire **automatically** during plan execution. The RuntimeExecutor triggers negotiations when the orchestration strategy requires capability scoring, sends handoff requests when an agent is degraded and a healthy replacement is found (auto-heal), and uses broadcast queries for consensus voting. The Communications Dashboard (6th Agent sub-tab) provides a read-only monitoring view of all inter-agent traffic with an SVG graph visualization and a unified activity feed.

Builtin agents:
- filesystem (filesystem.*)
- git (git.*)
- shell (shell.*/process.*)
- system (system.*)

8 agent blueprint templates for common roles.

Orchestration strategies:
- SINGLE, ROUND_ROBIN, CAPABILITY_SCORE, FALLBACK, PIPELINE

Workflow chains:
- Multi-step agent pipelines with output bridging, conditions, branching, parallel groups
- 35 built-in chain templates across 7 categories
- Optimization (dependency analysis → parallel groups), auto-assignment (capability-based), execution history, replay
- **Versioning model:** every chain carries an integer version counter and a `version_history` list of snapshots. Any mutation (step edit, drag-and-drop reassignment, conflict resolution, optimization, auto-assign) saves a snapshot of the current state before applying changes and increments the version. Rollback restores a previous snapshot but itself creates a new version, making it non-destructive. API: `PUT /workflow-chains/{id}` (versioned update), `GET /workflow-chains/{id}/versions` (history), `POST /workflow-chains/{id}/rollback` (revert)

### 4.10 RAG & Semantic Search Layer (Sprint 14)

Optional vector-based search for code understanding.

Subcomponents:

ChromaDB VectorStore (local, per-workspace collections)
SemanticIndexer (chunking, dedup, skip filters)
RAG-augmented chat (code snippets injected into LLM context)

### 4.11 Desktop Shell Layer (Sprint 38-46)

Native application wrapping via Tauri 2.

Features:
- Auto-spawns Python backend
- Frameless glassmorphic window chrome
- System tray (Show/Quit, close-to-tray)
- Auto-updater (GitHub Releases)
- Embedded Python distribution (zero-prerequisite installs)
- Cross-platform: Windows (MSI/NSIS), Linux (DEB/AppImage/RPM), macOS (DMG)

5. Runtime Flow

The canonical runtime flow is:

1. User submits intent
2. Neural Link forwards request
3. Intent Intake extracts structure
4. Planner generates plan
5. Plan Validator checks schema
6. Policy Engine evaluates each step
7. Approval Manager pauses risky steps if needed
8. Executor invokes tools
9. Tools return structured results
10. Events are emitted
11. Memory is updated
12. UI refreshes timeline and state

This flow must remain understandable and inspectable.

If the system cannot explain what happened, it is not mature enough.

6. Core Data Objects

MachinaOS should be built around a few canonical data models.

6.1 Intent

Represents what the user wants.

Fields may include:

intent_id

raw_input

normalized_goal

entities

constraints

ambiguity_score

risk_estimate

6.2 Plan

Represents a structured execution strategy.

Fields may include:

plan_id

intent_id

steps

created_at

planner_version

validation_status

6.3 Plan Step

Represents one atomic executable action.

Fields may include:

step_id

tool_name

arguments

requires_approval

expected_result

fallback_strategy

timeout

rollback_hint

6.4 Tool Result

Represents the actual outcome of a tool call.

Fields may include:

tool_name

status

output

error_code

message

duration_ms

6.5 Event

Represents a structured historical record.

Fields may include:

event_id

event_type

related_task

timestamp

payload

severity

6.6 Approval Request

Represents a gated action requiring user consent.

Fields may include:

approval_id

step_id

reason

preview

risk_level

expires_at

7. Trust Boundaries

MachinaOS must preserve strict trust boundaries.

7.1 The Model Is Not Trusted for Effects

The LLM can suggest actions but cannot be treated as evidence of execution.

7.2 Tool Outputs Are Trusted More Than Narration

System state must derive from tool results and event logs.

7.3 User Approval Overrides Automation for Risky Actions

No silent escalation.

7.4 Adapters Must Enforce Real Constraints

Do not rely on prompts alone for safety.

This is one of the central truths of the whole architecture:
prompts are guidance; boundaries must be enforced in code.

8. UI as Operational Surface

The MachinaOS UI should be treated as the visible face of runtime truth.

Key surfaces:

Dashboard

High-level system status, tool counts, recent state, approvals.

Neural Link

Intent entry point and conversational control surface.

Timeline

Real-time event and execution history.

Tool Registry

Discoverable catalog of system capabilities.

Approval Center

Human-in-the-loop control point for risky actions.

These are not cosmetic modules.
They are the operator’s windows into the system.

9. Dominant Workflow

The first fully mature workflow for MachinaOS should be:

developer environment orchestration

Canonical sequence:

open repo
inspect git state
open workspace
run tasks
read diagnostics
propose fixes
apply safe patch
rerun checks
summarize result

Why this workflow first:

high practical value

clear success criteria

rich tool interactions

strong visibility requirements

natural fit for approvals and rollback

If MachinaOS becomes excellent here, expansion into broader operating tasks becomes much easier.

10. Failure Model

Agentic systems fail constantly in weird little goblin ways. So MachinaOS must assume failure is normal.

Failure classes should include:

planner failure

schema failure

blocked action

missing tool

tool runtime error

timeout

partial completion

approval rejection

adapter incompatibility

Recovery strategies should include:

retry

fallback plan

step skip

user clarification

partial resume

rollback

safe abort

A mature system is not one that never fails.
It is one that fails legibly and recovers sanely.

11. Deployment Model

MachinaOS runs as a local system with multiple deployment options.

### Local development
```text
python -m uvicorn apps.api.server:app --host 127.0.0.1 --port 8100
```

### Desktop application (Tauri 2)
Self-contained native app bundling Python + all dependencies.
```text
cd desktop && npm run tauri build
```
Produces MSI/NSIS (Windows), DEB/AppImage/RPM (Linux), DMG (macOS).

### Docker
```text
docker-compose up -d  # MACHINA_MODE=demo for demo mode
```

### Architecture topology
```text
UI Client (Browser or Tauri Webview)
  ↕
Local API / FastAPI Runtime (port 8100)
  ↕
Planner / RuntimeExecutor / Policy Engine / Agent Coordination
  ↕
Tool Registry (40 tools, 7 domains)
  ↕
OS Adapters (filesystem, git, shell, process, browser, vscode, system)
  ↕
Host OS
```

### Storage
- SQLite (WAL mode): events.db, memory.db, telemetry.db, conversations.db, workspaces.db, workflows.db, agents.db, health.db
- JSONL for event stream dual-write
- ChromaDB (optional) for vector search
- File artifacts in `.machina/` directory

12. Architectural Principles

When tradeoffs appear, prefer:

inspectability over magic

small tools over broad tools

local execution over remote dependence

deterministic flows over clever improvisation

policy enforcement over prompt-based safety

one excellent workflow over many shallow ones

This is the anti-hype doctrine.

Very healthy.
Very unglamorous.
Exactly how real systems survive.

13. Evolution Path

MachinaOS has evolved through these phases:

Phase 1 — Agent Runtime ✅ (Sprints 1-10)
Intent intake, tools, events, approvals, local execution.

Phase 2 — Developer Cockpit ✅ (Sprints 11-16)
VS Code integration, Git intelligence, diagnostics, resumable tasks, workflows.

Phase 3 — Workspace Operating Layer ✅ (Sprints 17-37)
Persistent project memory, semantic navigation, multi-agent orchestration, workflow chains, RAG, conversation intelligence.

Phase 4 — Desktop Shell & Distribution ✅ (Sprints 38-49)
Tauri 2 native app, cross-platform installers, demo mode, visual Workflow Studio, agent templates, chain templates.

Current: 1964 tests, 491 build items, 49 sprints, v0.2.0.

Phase 5 — Next (Planned)
CI/CD pipeline for multi-platform builds, broader system integration, richer permissions.

14. Canonical Definition

MachinaOS is a local-first, intent-driven operating architecture that converts user goals into safe, observable, tool-executed actions across the development environment.

15. Final Engineering Statement

MachinaOS should never become:

an opaque assistant

a dashboard with AI paint on it

a planner without execution truth

an automation engine without safety

a memory system without structure

MachinaOS should become:

a trustworthy operating layer where models reason, tools act, events remember, and humans remain in control.