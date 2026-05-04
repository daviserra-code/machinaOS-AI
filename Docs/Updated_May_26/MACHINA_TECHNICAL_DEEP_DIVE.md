# Machina OS — Technical Deep Dive

> Reference document for NotebookLM. Covers architecture, module design, data models, API contracts, and implementation details.
> Based on Sprint 58+ (2148 tests, 544 build items, 218 API endpoints, 52 tools).

---

## 1. Architecture Overview

Machina OS is a **local-first, intent-driven operating layer**. It sits on top of an existing OS and translates natural-language goals into safe, auditable system actions. It is not a kernel. It does not replace the OS. It wraps it with intent awareness.

### Execution Pipeline

```
User Input (text)
  → Intake Parser          (heuristic-first, LLM fallback)
  → Planner                (deterministic templates or LLM plan generation)
  → Plan Validator         (schema enforcement, step limits, tool existence)
  → RuntimeExecutor        (contracts → guards → emitter → tool dispatch)
  → ToolRegistry           (typed specs, risk levels, execution limits)
  → Policy Engine          (risk-level gating, capability scopes)
  → StepRuntime            (step state machine, approval gates)
  → EventBus               (structured event envelope, SQLite + JSONL)
  → Response               (formatted output, streaming SSE)
```

Every layer has a defined input/output contract. No layer pretends to perform an action — every tool call must produce a real ToolResult.

### Core Module Locations

```
core/
  agent/         → MachinaCore orchestrator + intent intake
  planner/       → plan generation, validation, deterministic templates
  executor/      → legacy executor (superseded by RuntimeExecutor)
  runtime/       → RuntimeStore, TaskRuntime, StepRuntime, RuntimeExecutor
  contracts/     → canonical enums, prefixed ID generators, RuntimeSnapshot
  guards/        → TaskGuard, StepGuard, ApprovalGuard
  events/        → EventBus, EventEmitter
  tools/         → ToolRegistry, ToolSpec, built-in tools layer
  memory/        → MemoryStore (SQLite WAL), layered scopes
  policy/        → PolicyEngine, capability-based permissions
  llm/           → LLMClient, multi-provider adapter, LLMRouter
  agents/        → AgentPool, AgentBus, AgentStore, AgentDefinition
                    DelegationChain, AgentWorkflowChain
                    Consensus, Negotiation, Handoff, Health, ...
  security/      → EncryptionStore, CredentialScrubber, AuditLog, SecurityAnalyzer
  mcp/           → MCPClient, MCPToolBridge, MCPServerRegistry
  rag/           → VectorStore (ChromaDB), SemanticIndexer
  conversation/  → ConversationSession, ConversationStore
  workflow/      → WorkflowDefinition, WorkflowStore
  workspace/     → Workspace model, indexer, WorkspaceStore
  telemetry/     → TelemetryStore (plan/tool metrics, latency)
  demo/          → DemoMode, tool gating, DemoSessionManager, sanitizer
  personality/   → PersonalityProfile, preset injection
integrations/
  filesystem/    → 9 tools with path safety + reversibility
  git/           → 10 git tools
  shell/         → shell.run + shell.run_safe
  process/       → 4 process tools
  browser/       → 3 browser tools
  system/        → 4 system introspection tools (stdlib-only)
  github/        → 7 GitHub API tools (PAT-authenticated)
  vscode/        → 7 VS Code CLI tools
```

---

## 2. Intent Intake

**File**: `core/agent/intake.py`

The intake parser is heuristic-first. For any known deterministic intent, it bypasses the LLM entirely. LLM is only called if no heuristic matches.

### Routing Priority

1. **Heuristic patterns** — regex/substring matches for known intent keywords
2. **Dynamic tool-name routing** — detects dot-notation tool names (`system.info`, `filesystem.list`, etc.) against a runtime-populated `_tool_registry_names` set
3. **LLM intent classification** — sends raw input to LLM with structured output schema
4. **LLM tool-signal guardrail** — `_query_has_tool_signal()` last-resort check: if both heuristic and LLM return "general" but the query contains a registered tool name, forces task routing

### Deterministic Intents

```
list, read_file, write_file, delete_file, run_command, git_command,
list_processes, analyze_repository, dev_workflow, system_info,
grep, create_project, cleanup, find_and_read, semantic_search,
workflow, refactor, debug_issue, delegate, github_command
```

### Output: Intent Model

```python
class Intent(BaseModel):
    intent_id: str          # "int_<uuid>"
    intent: str             # e.g. "list"
    entities: dict          # extracted entities {"path": ".", "pattern": "*.py"}
    constraints: dict       # e.g. {"max_results": 20}
    ambiguity_score: float  # 0.0–1.0; triggers clarification if > 0.7
    risk_level: RiskLevel
```

### Path Normalization

Before routing, intake normalizes natural-language path references:
- `"current directory"`, `"here"`, `"this folder"` → `"."`
- Resolves relative references against workspace root

---

## 3. Planner

**File**: `core/planner/planner.py`

The planner generates a `Plan` (ordered list of `PlanStep`) from an `Intent`. It is hybrid: deterministic templates take priority, LLM is the fallback for open-ended intents.

### Plan Model

```python
class Plan(BaseModel):
    plan_id: str
    task_id: Optional[str]
    intent: Intent
    steps: List[PlanStep]
    planner_version: str
    validation_status: ValidationState

class PlanStep(BaseModel):
    id: str                    # "step_<uuid>"
    index: int
    description: str
    tool: str                  # must be registered in ToolRegistry
    arguments: dict
    requires_approval: bool
    timeout: Optional[int]     # seconds; overrides global default
    rollback_hint: Optional[str]  # tool to call on failure
    expected_output: Optional[str]
    fallback: Optional[str]    # tool to try if primary fails
    delegate_to: Optional[str] # agent_id for scoped delegation
    risk_level: RiskLevel
    policy_decision: PolicyDecision
    last_transition_at: Optional[datetime]
    reason: Optional[str]
```

### Plan Validation

`PlanValidator` enforces before execution:
- Max 12 steps per plan
- All tools must exist in ToolRegistry
- Required params must be present
- HIGH-risk tools force `requires_approval=True`
- Oversized arguments truncated
- Invalid fallback tools cleared

### Deterministic Templates

Known intents skip LLM and use pre-built templates. Examples:

**`dev_workflow`** (9 steps):
```
filesystem.tree → git.status → vscode.open_workspace → vscode.run_task
→ vscode.read_diagnostics → system.info → system.memory → system.disk → summarize
```

**`analyze_repository`** (7 steps):
```
filesystem.tree → git.status → git.log → vscode.read_diagnostics
→ filesystem.grep (TODO/FIXME) → system.info → summarize
```

**`create_project`**: scaffolds Python or JS project structure with files + tests.

**`cleanup`**: tree → git.status → system.disk → temp file search.

**`debug_issue`**: diagnostics → git.status → git.log → diff → grep → summary.

### Workspace Context Injection

When the LLM planner is used, workspace intelligence is injected into the system prompt:
- Detected languages and frameworks
- Key files (entry points, configs, READMEs)
- Active git branch

---

## 4. Guards & State Machines

**File**: `core/guards/`

All state transitions are validated by guard classes before being applied. No direct field mutations are allowed.

### TaskGuard

Valid task state transitions per `MACHINA_STATE_MACHINE §4.4`:

```
CREATED → INTAKE_COMPLETE → PLANNED → VALIDATED
        → WAITING_APPROVAL → READY → EXECUTING
        → PAUSED (from EXECUTING)
        → COMPLETED (from EXECUTING)
        → FAILED (from EXECUTING, WAITING_APPROVAL)
        → ABORTED (from any non-terminal)
        → ROLLING_BACK → ROLLED_BACK
```

Terminal states: `COMPLETED`, `FAILED`, `ABORTED`, `ROLLED_BACK`.

### StepGuard

Valid step state transitions per `§6.4`:

```
PENDING → BLOCKED | WAITING_APPROVAL | READY
READY → RUNNING
RUNNING → SUCCEEDED | FAILED
FAILED → READY (retry)
PENDING/READY/RUNNING → SKIPPED
SUCCEEDED/FAILED → ROLLED_BACK
```

### ApprovalGuard

One-shot lifecycle:
```
PENDING → GRANTED | DENIED | EXPIRED | CANCELLED
```
All terminal. Once resolved, no further transitions.

---

## 5. Runtime Infrastructure

### RuntimeStore

**File**: `core/runtime/store.py`

Hybrid persistence:
- **SQLite** (WAL mode) for tasks, steps, approvals, and snapshots
- **JSONL** for event stream (dual-write)

Tables: `tasks`, `steps`, `approvals`, `snapshots`

### TaskRuntime

**File**: `core/runtime/coordinator.py`

Wires together: `contracts → guards → emitter → store`

Operations:
- `create_task()` — creates Task, validates initial state, persists, emits `task_created`
- `transition_task()` — validates via TaskGuard, persists, emits state change event
- `request_approval()` — creates ApprovalRequest with TTL (default 5 min), persists, emits `approval_requested`
- `grant_approval()` / `deny_approval()` — validates via ApprovalGuard, updates step status, resumes task
- `expire_overdue_approvals()` — ScheduledTask sweeps pending approvals every 30s

### StepRuntime

**File**: `core/runtime/step_runtime.py`

- `register_steps()` — creates PlanStep records in SQLite for a plan
- `transition_step()` — validates via StepGuard, persists, emits `step_*` events
- `_sync_task_status()` — bidirectional sync: when all steps resolve, updates parent task status; resumes task from WAITING_APPROVAL when no steps need approval

### RuntimeExecutor

**File**: `core/runtime/executor.py`

The primary execution dispatcher. Replaces the legacy Executor.

```python
async def run_task(task_id, plan, auto_approve=False) -> List[StepResult]
async def run_step(task_id, step) -> StepResult
async def run_workflow_chain(chain) -> dict
async def run_workflow_chain_parallel(chain) -> dict
async def schedule_task(tool, arguments, priority) -> dict
async def auto_execute_task(item_id) -> dict
async def auto_execute_agent_queue(agent_id) -> List[dict]
async def replay_workflow_chain(source_execution_id, overrides) -> dict
```

**`run_step` execution flow**:
1. Policy check → step status: `WAITING_APPROVAL` (HIGH risk) or `READY`
2. If `delegate_to` set: check `chain.would_cycle()`, check agent `accepts_tool()`
3. If health-aware routing: skip OFFLINE agents, reroute to healthy candidate
4. Invoke tool via `ToolRegistry.invoke()`
5. Capture `ToolResult`, transition step to `SUCCEEDED` or `FAILED`
6. Record capability score + reputation to agent memory
7. Record health check to `AgentBus`
8. Record performance trend to `HealthStore`
9. Bridge output to downstream steps via `output_key`

### Error Classification & Retry

```python
class ErrorClass(str, Enum):
    TRANSIENT = "transient"     # retry with backoff
    PERMANENT = "permanent"     # no retry
    PERMISSION = "permission"   # policy block
    NOT_FOUND = "not_found"     # missing resource
```

Transient errors get exponential backoff retry (configurable). Plans with mixed success/failure continue to completion (partial plan recovery).

---

## 6. Tool Registry

**File**: `core/tools/registry.py`

Central registry of all available tools. Every tool has a `ToolSpec`:

```python
class ToolSpec(BaseModel):
    name: str                   # "filesystem.list"
    description: str
    params: Dict[str, Any]      # typed parameter schema
    output_schema: Dict[str, Any]
    risk_level: RiskLevel       # LOW / MEDIUM / HIGH / CRITICAL
    requires_approval: bool
    timeout: int                # seconds (default 120)
    max_output_size: int        # bytes (default 1 MB)
    handler: Callable
```

`ToolRegistry.invoke(name, arguments)` enforces:
- Tool existence check
- Demo mode gating (`is_tool_gated()`)
- Hard timeout (120s default)
- Output truncation (1 MB)
- Structured error codes on failure

### Structured Error Codes

Every `ToolResult.error_code` is one of:
```
FILE_NOT_FOUND, PERMISSION_DENIED, TIMEOUT, UNKNOWN_ERROR,
AGENT_TOOL_DENIED, DELEGATION_CYCLE, CONSENSUS_REJECTED,
DEMO_TOOL_BLOCKED, AGENT_HEALTH_DEGRADED, ...
```

### Tool Domains & Counts

| Domain | Count | Tools |
|--------|-------|-------|
| `filesystem` | 9 | list, read_file, write_file, move, delete, tree, search, grep, semantic_search |
| `git` | 12 | status, log, diff, checkout, clone, branch, pull, push, commit, stash, tag, merge |
| `shell` | 2 | run, run_safe |
| `process` | 4 | list, info, start, stop |
| `browser` | 3 | open_url, search_files, find_recent |
| `system` | 5 | status, info, memory, disk, env |
| `vscode` | 7 | open_workspace, open_file, list_extensions, install_extension, run_task, diff, read_diagnostics |
| `github` | 7 | list_repos, repo_info, list_branches, list_issues, list_prs, create_issue, clone |
| **MCP** | dynamic | `mcp.<server>.<tool>` namespace; added at runtime |

### Path Safety

`_validate_path(path, write=False)`:
- **Reads**: allowed in system directories (`C:\Program Files`, `/usr`, etc.)
- **Writes/deletes**: blocked outside workspace root; blocked in system directories
- Workspace root set via `set_workspace_root()` at startup
- Shell safety: blocks privilege escalation (`sudo`, `runas`, etc.) and destructive commands

### Filesystem Reversibility

`filesystem.write_file` backs up any existing file as `<path>.machina_bak` before overwriting.

---

## 7. Policy Engine

**File**: `core/policy/engine.py`

Risk-level based decision engine.

### Risk Levels → Decisions

```
CRITICAL → PolicyDecision.BLOCK
HIGH     → PolicyDecision.REQUIRE_APPROVAL
MEDIUM   → PolicyDecision.REQUIRE_APPROVAL  (configurable)
LOW      → PolicyDecision.ALLOW
```

### Capability Scopes

Each tool is mapped to a capability scope:

```
filesystem.read     → filesystem.read
filesystem.write    → filesystem.write
filesystem.delete   → filesystem.delete
shell.run           → shell.execute
process.stop        → process.control
git.push, git.clone → git.write
```

Permission profiles:
- `DEFAULT_GRANTS` — all capabilities enabled
- `READONLY_GRANTS` — only read capabilities

Hierarchical: granting `filesystem` covers all `filesystem.*` sub-caps.

---

## 8. Event System

**File**: `core/events/`

### Event Envelope

Every event follows the canonical schema (schema_version `"1.0"`):

```python
class Event(BaseModel):
    event_id: str           # "evt_<uuid>"
    event_type: str         # "task_created", "tool_started", etc.
    payload: dict
    source: str             # "core" | "executor" | "planner" | "intake" | "validator" | "policy"
    severity: str           # "INFO" | "WARN" | "ERROR" | "CRITICAL"
    schema_version: str     # "1.0"
    timestamp: datetime
    sequence: int           # monotonic counter, thread-safe
    task_id: Optional[str]
    approval_id: Optional[str]
    workspace_id: Optional[str]
    correlation_id: Optional[str]
    trace_id: Optional[str]
    actor: Optional[str]
```

### EventBus

- `emit(event_type, payload, **kwargs)` — keyword-only args for envelope fields
- SQLite persistence (12-column schema, WAL mode) + JSONL dual-write
- `query_events(type, source, severity, plan_id, limit, offset)` — filtered queries
- `event_types()`, `event_sources()`, `event_count()` — metadata methods
- WebSocket forwarding: connected clients receive all emitted events live

### EventEmitter

Canonical factory in `core/events/emitter.py`. Wraps EventBus with domain-specific `emit_*` helpers:
- `emit_task_created()`, `emit_step_started()`, `emit_tool_finished()`, etc.
- Standalone mode: EventEmitter can operate without a bus (stores events locally)

---

## 9. Memory System

**File**: `core/memory/store.py`

SQLite-backed (WAL mode) layered key-value store with explicit scope separation.

### Memory Scopes

| Scope | Lifetime | Use |
|-------|----------|-----|
| `session` | Cleared on reset | Ephemeral task context |
| `task` | Per task_id | Step outputs, intermediate state |
| `project` | Persistent | Cross-session project context |
| `preferences` | Never auto-cleared | User settings, LLM config |
| `agent` | Per agent_id | `agent_id:key` namespaced partitions |
| `telemetry` | Separate store | Metrics (telemetry.db) |

### Agent Memory

Per-agent memory is isolated using the `agent` scope with `agent_id:key` pattern:
- `set_agent_memory(agent_id, key, value)`
- `get_agent_memory(agent_id, key, default=None)`
- `list_agent_keys(agent_id)` → list of keys
- `clear_agent_memory(agent_id)` → deletes all keys for agent
- Different agents' memory is completely independent

### Capability & Reputation Storage

Both `CapabilityScore` and `AgentReputation` are stored as JSON in agent memory:
- Key: `cap:<tool>` → `CapabilityScore` JSON
- Key: `rep:global` → `AgentReputation` JSON

---

## 10. Multi-Agent Coordination

**File**: `core/agents/`

### AgentDefinition

```python
class AgentDefinition(BaseModel):
    agent_id: str                  # "agent_<uuid>" or custom
    name: str
    capabilities: List[str]        # e.g. ["filesystem", "read", "write"]
    tool_filter: List[str]         # fnmatch globs e.g. ["filesystem.*"]
    system_prompt: Optional[str]
    enabled: bool = True
```

`accepts_tool(tool_name)` → bool: checks tool against `tool_filter` using fnmatch.

### AgentPool

In-memory registry with optional bus reference for health-aware routing.

Key methods:
- `register(agent)` / `unregister(agent_id)` — emits lifecycle events
- `find_by_capability(capability)` → agents with matching capability
- `find_for_intent(intent)` → agents capable of handling intent
- `candidates_for_tool(tool_name)` → sorted list (OFFLINE excluded, DEGRADED deprioritized)
- `select_agent(tool, strategy)` → single agent per strategy
- `best_agent_for_tool(tool)` → highest capability confidence from memory

### Specificity Scoring

```python
def score_agent_for_tool(agent, tool_name) -> float:
    for pattern in agent.tool_filter:
        if pattern == tool_name:        return 1.0           # exact match
        if fnmatch(tool_name, pattern): return 0.3 + 0.7/len(pattern)  # glob
    if "*" in agent.tool_filter:        return 0.1           # open filter
    return 0.0
```

### AgentBus

Pub/sub message bus for all inter-agent communication. The AgentBus provides 6 communication channels that form the backbone of multi-agent coordination:

**1. Bus Messages (pub/sub)** — Low-level event transport. Agents publish messages with a type and payload; other agents subscribe to specific types or agent IDs. Every protocol below emits bus events as side effects. History is capped to prevent unbounded growth.

**2. Agent Requests** — Point-to-point, request-response interactions. Agent A sends a request to Agent B with an `action` and `payload`. Agent B responds. Lifecycle: `PENDING → DELIVERED → RESPONDED` (or `TIMEOUT` / `FAILED`). Each request has a `correlation_id` for threading.

**3. Broadcast Queries** — One-to-many polling. An agent asks a question to a list of target agents and collects responses. Supports configurable `timeout_ms` (0 = no timeout). Responses can be aggregated using 4 strategies: `ALL` (dict of all), `FIRST` (first value), `MERGE` (merged dict), `MAJORITY` (most common). Lifecycle: `PENDING → COLLECTING → COMPLETED` (or `EXPIRED`).

**4. Negotiations** — Bilateral tool ownership resolution. When two or more agents can handle a tool, a negotiation determines who executes. Lifecycle: `PROPOSED → COUNTERED → ACCEPTED/REJECTED/RESOLVED`. Supports multi-round counter-proposals (max 10 rounds), priority-based auto-resolution (lower priority value wins), and `auto_counter()` which picks the best alternative agent by capability confidence.

**5. Handoffs** — Formal task transfer with preconditions and constraints. Agent A transfers responsibility for a step to Agent B. Lifecycle: `REQUESTED → ACCEPTED → EXECUTING → COMPLETED` (or `DECLINED` / `FAILED` / `CANCELLED`). Used by the auto-heal system when a degraded agent is replaced.

**6. Collaborations** — Shared multi-agent sessions. Multiple agents join a session around a `task_id`, share a context dict (key-value store), and coordinate work. Lifecycle: create → join/leave → set_context → close.

**When do these fire?** These protocols are triggered automatically by the RuntimeExecutor during plan execution:
- **CAPABILITY_SCORE** strategy → negotiations determine tool ownership
- **FALLBACK** strategy → handoffs when Agent A fails and Agent B takes over
- **Consensus-aware execution** → broadcast queries collect agent votes
- **Auto-heal** → handoffs when degraded agents are replaced by healthy ones
- **Pipeline execution** → bus messages carry output between chained agents

The Communications Dashboard (API: `GET /agents/communications/feed` and `GET /agents/communications/graph`) provides a read-only unified view of all inter-agent traffic.

```python
class AgentBus:
    # Core messaging
    send(message: AgentMessage)
    broadcast(source, type, payload)
    subscribe(handler, agent_id=None, message_type=None)

    # Delegation
    delegate(chain, from_agent, to_agent, tool, step_id)
    create_chain(chain_id) / get_chain(id) / remove_chain(id)

    # Consensus
    request_consensus(question, candidates, strategy, min_voters) -> ConsensusRequest
    cast_vote(request_id, agent_id, value, weight, reason)
    resolve_consensus(request_id) -> ConsensusRequest

    # Negotiation
    start_negotiation(initiator, responder, tool, priority, reason, proposed_agent)
    counter_negotiation(id, counter_agent, counter_reason)
    accept_negotiation(id) / reject_negotiation(id) / resolve_negotiation_by_priority(id)
    auto_counter(id) -> NegotiationProposal  # picks best alt by capability confidence

    # Handoffs
    request_handoff(from_agent, to_agent, tool, preconditions, constraints, reason)
    accept_handoff(id) / decline_handoff(id, reason) / complete_handoff(id) / fail_handoff(id, reason)

    # Health monitoring
    record_health_check(agent_id, success, latency_ms, error=None, error_code=None)
    get_agent_health(agent_id) -> AgentHealthRecord
    set_agent_status(agent_id, status)
    auto_heal(agent_id) -> Optional[AgentDefinition]

    # Workflow chains
    create_workflow_chain(chain) / get_workflow_chain(id) / list_workflow_chains()
    update_workflow_chain(id, new_steps, description) / rollback_workflow_chain(id, target_version)
    optimize_chain(chain) -> dict   # dependency graph → parallel groups
    apply_optimization(chain_id)
    auto_assign_chain(chain_id) / negotiate_pipeline(chain, pool)
    create_chain_from_template(template_name) -> AgentWorkflowChain

    # Broadcast queries
    broadcast_query(from_agent, question, target_agents, timeout_ms=0) -> BroadcastQuery
    respond_to_query(query_id, agent_id, payload) / complete_query(query_id)
    aggregate_broadcast(query_id, strategy) -> BroadcastAggregation
    expire_overdue_queries() -> List[BroadcastQuery]

    # Task queue
    enqueue_task(agent_id, tool, arguments, priority) -> AgentTaskItem
    dequeue_task(agent_id) -> Optional[AgentTaskItem]
    complete_task_item(item_id, result) / fail_task_item(item_id, error)

    # Collaborations
    create_collaboration(task_id, participants) -> CollaborationSession
    join_collaboration(session_id, agent_id) / leave_collaboration(session_id, agent_id)
    set_collaboration_context(session_id, key, value)

    # Communications feed / graph
    # ... plus consensus patterns, chain executions, replays, announcements, requests, threads
```

### AgentStore

SQLite-backed persistence (`agents.db`, WAL mode) for user-created agents. Built-in agents (`agent_filesystem`, `agent_git`, `agent_shell`, `agent_system`) are never written to the store.

### DelegationChain

```python
class DelegationChain:
    max_depth: int = 5
    push(agent_id) -> bool       # returns False if would_cycle or would_exceed_depth
    pop() -> Optional[str]
    would_cycle(agent_id) -> bool
    would_exceed_depth() -> bool
```

---

## 11. Consensus System

### Models

```python
class ConsensusRequest(BaseModel):
    request_id: str              # "cons_<uuid>"
    question: str
    candidates: List[str]        # agent_ids
    votes: Dict[str, Vote]
    strategy: ConsensusStrategy  # MAJORITY | UNANIMOUS | WEIGHTED
    min_voters: int
    status: ConsensusStatus      # PENDING | RESOLVED | REJECTED | EXPIRED

class Vote(BaseModel):
    agent_id: str
    value: VoteValue             # APPROVE | REJECT | ABSTAIN
    weight: float                # 0.0–1.0
    reason: Optional[str]
    cast_at: datetime
```

### Resolution Logic

```python
def resolve(self) -> ConsensusStatus:
    if strategy == MAJORITY:
        weighted_approvals = sum(v.weight for v in votes if v.value == APPROVE)
        weighted_rejections = sum(v.weight for v in votes if v.value == REJECT)
        return RESOLVED if weighted_approvals > weighted_rejections else REJECTED
    elif strategy == UNANIMOUS:
        return RESOLVED if all(v.value == APPROVE for v in votes) else REJECTED
    elif strategy == WEIGHTED:
        net = sum(v.weight if v.value==APPROVE else -v.weight for v in votes)
        return RESOLVED if net > 0 else REJECTED
```

### Consensus-Aware Execution Flow

In `RuntimeExecutor.run_step_with_consensus()`:
1. Check `should_skip_consensus(tool)` — skip if pattern has ≥10 samples and >95% approval
2. Find candidates for tool via AgentPool
3. If < 2 candidates: skip consensus
4. Create consensus request
5. Auto-vote each candidate: `confidence ≥ 0.3 → APPROVE` (weight=confidence); else REJECT
6. Resolve → RESOLVED: proceed; REJECTED: return CONSENSUS_REJECTED error
7. Record outcome via `record_consensus_outcome(tool, approved)`

### Consensus Pattern Learning

```python
class ConsensusPatternScore:
    pattern: str      # tool name
    approvals: int
    rejections: int

    @property
    def should_skip_consensus(self) -> bool:
        return self.total >= 10 and self.approval_rate > 0.95
```

---

## 12. Negotiation Protocol

### Lifecycle

```
PROPOSED → COUNTERED (repeat up to max_rounds) → ACCEPTED | REJECTED | RESOLVED
         → WITHDRAWN
         → FAILED
```

### Model

```python
class NegotiationProposal(BaseModel):
    negotiation_id: str
    initiator: str          # agent_id
    responder: str          # agent_id
    tool: str
    phase: NegotiationPhase
    priority: NegotiationPriority   # CRITICAL=1, HIGH=2, NORMAL=3, LOW=4
    proposed_agent: str
    counter_agent: Optional[str]
    max_rounds: int = 3
    current_round: int = 0
    winner: Optional[str]   # set on RESOLVED/ACCEPTED

    @property
    def is_terminal(self) -> bool:
        return self.phase in {ACCEPTED, REJECTED, RESOLVED, FAILED, WITHDRAWN}
```

### Priority Resolution

`resolve_by_priority()`: lower priority value wins (CRITICAL < HIGH < NORMAL < LOW). Ties → initiator wins.

### Auto-Counter

`suggest_counter_agents(negotiation, pool, bus)` ranks alternative agents by capability confidence, excluding the proposed agent. `auto_counter()` picks the best and submits a counter-proposal.

---

## 13. Agent Workflow Chains

### Models

```python
class AgentWorkflowStep(BaseModel):
    agent_id: Optional[str]
    tool: str
    arguments: dict = {}
    description: str = ""
    output_key: Optional[str]    # stores step output for downstream
    input_from: Optional[str]    # reads from prior step's output_key
    condition: Optional[str]     # "output_key:field op value"
    branch_to: Optional[str]     # agent_id to reroute to if condition fails
    parallel_group: Optional[str]  # group key for concurrent execution

class AgentWorkflowChain(BaseModel):
    chain_id: str               # "wc_<uuid>"
    name: str
    description: str = ""
    steps: List[AgentWorkflowStep]
    version: int = 1
    version_history: List[dict] = []
    updated_at: Optional[datetime]

    def snapshot(self) -> dict   # serializable state capture
    def update_steps(self, new_steps, description) -> None   # increments version
    def rollback(self, target_version) -> bool
```

#### Versioning Behaviour

Every workflow chain maintains an append-only version history. Mutations follow this sequence:

1. **snapshot()** — serialises the current `{version, name, steps, timestamp}` into a dict.
2. **update_steps(new_steps, description)** — calls `snapshot()`, appends it to `version_history`, replaces `steps`, increments `version`, updates `updated_at`.
3. **rollback(target_version)** — finds the snapshot where `snapshot["version"] == target_version`. If found: saves the current state via `snapshot()` first (so nothing is lost), restores steps/name from the target snapshot, increments `version` (rollback is a forward operation), returns `True`. If not found: returns `False`.

This means:
- `version_history` is **append-only** — entries are never deleted
- Rollback itself creates a new version (you can undo a rollback)
- Any action that calls `update_steps()` triggers a version bump: UI edits, drag-and-drop lane reassignment, conflict resolution, apply-optimization, auto-assign

Persistence: `ChainStore` (SQLite, WAL mode) serialises both `steps` and `version_history` as JSON columns. `AgentBus` auto-persists on every create/update/rollback/delete.

```text
Version timeline example:
  v1 → created with steps [A, B, C]
  v2 → user edits to [A, B, D]       (v1 snapshot saved)
  v3 → auto-assign changes agent on B (v2 snapshot saved)
  v4 → rollback to v1 → [A, B, C]    (v3 snapshot saved)
       version_history now has 4 entries, all recoverable
```

### Output Bridging

`_bridge_step_input(step, collected_outputs)`:
1. If `step.input_from` set: look up collected outputs for that key
2. Resolve path from `files`, `matches`, string, or list fields
3. Inject `_prior_output` key into step arguments
4. Forward all non-underscore dict keys via `setdefault`

### Condition Evaluation

`evaluate_condition(condition_str, collected_outputs)`:
- Format: `output_key:field op value`
- Operators: `==`, `!=`, `contains`, `not_empty`
- Returns `True` (step should run) or `False` (skip or branch)

### Parallel Execution

`run_workflow_chain_parallel()`:
1. Group steps by `parallel_group` key
2. Steps with `parallel_group=None` form individual groups
3. Process groups sequentially; within each group: `asyncio.gather(*[run_step(s) for s in group])`
4. Falls back to sequential if no groups defined

### Chain Optimization

`optimize_chain(chain)`:
1. Build dependency graph from `output_key` / `input_from` references
2. Topological sort
3. Assign parallel group labels to independent steps
4. Returns `{ "groups": [...], "assignments": {...} }`

### Built-in Templates

35 chain templates available. Examples:

| Template | Steps | Key Tools |
|----------|-------|-----------|
| `code-review` | 4 | tree → git.status → grep → read README |
| `security-audit` | 3 | grep secrets → grep insecure → tree |
| `release-readiness` | 4 | grep TODO → grep debug → memory → disk |
| `security-deep-scan` | 5 | grep secrets → grep insecure → grep JWT → tree → log |
| `hotfix-workflow` | 4 | grep error → read files → git.status → git.diff |
| `pr-readiness-check` | 5 | git.status → git.diff → grep TODO → grep debug → disk |

---

## 14. Capability Learning & Reputation

### CapabilityScore

```python
class CapabilityScore(BaseModel):
    agent_id: str
    tool: str
    successes: int = 0
    failures: int = 0
    total_duration_ms: int = 0
    last_error_code: Optional[str] = None
    error_counts: Dict[str, int] = {}

    @property
    def confidence(self) -> float:
        if self.successes + self.failures == 0:
            return 0.5    # neutral prior
        rate = self.successes / (self.successes + self.failures)
        sample_factor = min(1.0, (self.successes + self.failures) / 20)
        return rate * sample_factor
```

### AgentReputation

```python
class AgentReputation(BaseModel):
    agent_id: str
    total_successes: int = 0
    total_failures: int = 0
    total_tasks: int = 0
    total_duration_ms: int = 0
    tools_used: Dict[str, int] = {}       # tool → invocation count
    recent_outcomes: List[bool] = []      # last 50 outcomes

    @property
    def reputation_score(self) -> float:
        if self.sample_size == 0: return 0.5
        lifetime = self.success_rate
        recent = self.recent_success_rate
        sample_conf = min(1.0, self.sample_size / 20)
        return (0.4 * lifetime + 0.6 * recent) * sample_conf
```

Both are persisted to agent memory (JSON in `agent` scope) after each delegated execution.

---

## 15. Agent Health Monitoring

### AgentHealthRecord

```python
class AgentHealthRecord(BaseModel):
    agent_id: str
    status: AgentHealthStatus       # ONLINE | DEGRADED | OFFLINE
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    total_checks: int = 0
    avg_latency_ms: float = 0.0
    recent_latencies: List[float] = []   # rolling window (20)
    last_error: Optional[str] = None
    degraded_since: Optional[datetime]
    offline_since: Optional[datetime]
```

### Auto-Transition Rules

```
consecutive_failures >= 3  → DEGRADED
consecutive_failures >= 6  → OFFLINE
consecutive_successes >= 3 AND status != ONLINE → ONLINE (recovery)
recent_latency_avg > baseline_avg * 3.0 → DEGRADED (latency spike)
```

### HealthStore

SQLite (`health.db`) with three tables:
- `health_checks` — individual check events
- `health_snapshots` — periodic full-record snapshots (restored on restart)
- `performance_trends` — time-series (reputation_score, success_rate, avg_latency_ms, health_status)

On startup: `_load_health_snapshots()` restores last-known status for each agent.

---

## 16. Security Modules

**File**: `core/security/`

### EncryptionStore

- AES-256-GCM encryption with PBKDF2 key derivation (600,000 iterations, SHA-256)
- SQLite-backed `secrets` table; per-secret random nonces
- Graceful fallback: XOR + HMAC authenticated encryption when `cryptography` package unavailable
- API: `store_secret(name, value)`, `retrieve_secret(name)`, `delete_secret(name)`, `list_secrets()`

### CredentialScrubber

20+ regex patterns detecting:
- API keys: OpenAI (`sk-...`), GitHub (`ghp_...`), GitLab, Slack, Google
- AWS (`AKIA...`), Azure storage keys
- JWTs (three base64 segments)
- Bearer tokens, private key blocks, connection strings (MongoDB, Postgres, MySQL)
- Custom patterns and literals registerable at runtime

`scrub_text(text) -> str` — replaces matches with `[REDACTED]`

`scrub_output(data) -> Any` — recursively scrubs dicts/lists/strings

Wired into `_plan_to_response()` in MachinaCore for automatic output sanitization.

### AuditLog

SOC 2-compatible immutable audit trail with SHA-256 hash chains:

```python
class AuditEntry(BaseModel):
    audit_id: str
    timestamp: datetime
    actor: str
    action: str
    resource: str
    outcome: str        # "success" | "failure" | "blocked"
    detail: str
    risk_level: str
    chain_hash: str     # SHA-256 of (prev_hash + current_entry_fields)
```

`verify_chain()` → validates entire hash chain for tamper detection.

### SecurityAnalyzer

14 vulnerability patterns with CWE IDs:
- SQL injection (CWE-89), XSS (CWE-79), SSRF (CWE-918)
- Command injection (CWE-78), path traversal (CWE-22)
- JWT issues (CWE-347), hardcoded secrets (CWE-798)
- Eval/exec usage (CWE-95), insecure deserialization (CWE-502)

`analyze(code) -> List[SecurityFinding]`

```python
class SecurityFinding(BaseModel):
    cwe_id: str
    severity: str       # CRITICAL | HIGH | MEDIUM | LOW | INFO
    description: str
    line: Optional[int]
    snippet: Optional[str]
```

---

## 17. MCP Protocol

**File**: `core/mcp/`

### MCPClient

JSON-RPC 2.0 client over stdio transport:
- Spawns MCP server as subprocess
- Initialize handshake: protocol version `2024-11-05`
- Methods: `list_tools`, `call_tool`, `list_resources`, `read_resource`, `list_prompts`, `get_prompt`

### MCPToolBridge

Converts MCP tool definitions to Machina `ToolSpec`:
- Namespace: `mcp.<server_name>.<tool_name>`
- `inputSchema.properties` → `params` dict
- Risk level: MEDIUM by default
- Async-to-sync wrapper for MCP handler calls
- Registered into `ToolRegistry` on `connect()`

### MCPServerRegistry

SQLite-backed (`mcp_servers.db`) server configuration store:

```python
class MCPServerConfig(BaseModel):
    server_id: str
    name: str
    transport: str        # "stdio" | "http"
    command: Optional[str]   # for stdio: executable + args
    args: List[str] = []
    env: Dict[str, str] = {}
    url: Optional[str]       # for HTTP transport
    enabled: bool = True
    auto_connect: bool = False
```

---

## 18. RAG / Semantic Search

**File**: `core/rag/`

### VectorStore

ChromaDB wrapper with graceful degradation:
- Collection per workspace: `ws_<workspace_id>`
- Cosine similarity HNSW space
- Returns `None` when ChromaDB not installed

### SemanticIndexer

```python
class SemanticIndexer:
    chunk_size: int = 800
    chunk_overlap: int = 200

    async def index_file(self, path, workspace_id)
    async def index_directory(self, directory, workspace_id, patterns=None)
    def should_index(self, path) -> bool    # skip binaries, build artifacts, etc.
```

Content-hash deduplication: files are re-indexed only if content changes.

Indexing is **explicit-only** (`POST /rag/index`). No auto-indexing during `run()`. Lazy initialization: ChromaDB client created on first RAG access.

RAG-augmented chat: `_get_rag_context()` injects top-N relevant code snippets into the LLM conversational system prompt.

---

## 19. LLM Subsystem

**File**: `core/llm/`

### LLMClient

```python
class LLMClient:
    async def chat(messages, model=None, **kwargs) -> str
    async def chat_stream(messages, model=None) -> AsyncIterator[str]
    async def generate(prompt, model=None) -> str
    async def list_models() -> List[str]
    async def check_availability() -> dict  # {reachable, detail, error_type}
    def reconfigure(base_url=None, model=None, api_key=None, provider=None)
```

`check_availability()` distinguishes:
- `connection_refused` — server not running
- `timeout` — service starting up or overloaded
- `auth_error` — invalid API key

### Provider Support

| Provider | Auto-Detection | Auth Header | Endpoint |
|----------|---------------|-------------|----------|
| Ollama | `localhost:11434` | none | `/api/chat` |
| OpenAI | `api.openai.com` | `Authorization: Bearer` | `/v1/chat/completions` |
| Gemini | `generativelanguage.googleapis.com` | `x-goog-api-key` | `/v1beta/...` |
| Claude | `api.anthropic.com` | `x-api-key` + `anthropic-version` + `anthropic-beta: prompt-caching-2024-07-31` | `/v1/messages` |
| OpenRouter | `openrouter.ai` | `Authorization: Bearer` + `HTTP-Referer` + `X-Title` | `/v1/chat/completions` |
| LM Studio | `localhost:1234` | none | `/v1/chat/completions` |

Config persistence: saved to `preferences` scope, restored on `MachinaCore` startup via `_apply_saved_llm_config()`.

Split timeouts: `httpx.Timeout(connect=10, read=120)` prevents premature timeout during Ollama model loading.

### Claude-Specific Optimisations

- **Prompt caching (Claude only).** `_chat_claude` and `_stream_claude` wrap the system prompt in a `[{"type": "text", "text": ..., "cache_control": {"type": "ephemeral"}}]` block, activated by the `anthropic-beta: prompt-caching-2024-07-31` header. Repeated calls (intake → planner → conversation) hit the cache and report `cache_read_input_tokens > 0`.
- **Native tool use.** `LLMClient.chat_with_tools(messages, tools, *, tool_choice)` posts to `/v1/messages` with a `tools` array and optional `tool_choice`. Returns `{"content": str | None, "tool_calls": [{"name", "id", "input"}]}`. Non-Claude providers transparently fall back to plain `chat()` with empty `tool_calls`.
- **Structured planner.** `create_plan_llm_native_tools()` (in `core/planner/planner_llm.py`) defines a `_CREATE_PLAN_TOOL` JSON schema and forces Claude to fill it via `tool_choice={"type": "tool", "name": "create_plan"}`. Plans returned this way have `planner_version="claude-tool-use-v1"` and never trigger JSON-parse fallbacks. Other providers route through the legacy `create_plan_llm()` path unchanged.

### LLMRouter

Multi-route fallback:
```python
class LLMRoute(BaseModel):
    name: str
    capabilities: List[str]   # "general", "fast", "planning", "conversation", "coding"
    client: LLMClient
    priority: int

class LLMRouter:
    add_route(route)
    async def route(capability) -> LLMClient    # priority-ordered fallback
```

---

## 20. Background Services

**File**: `core/agents/` + `MachinaCore`

### ScheduledTask

```python
async def schedule_task(coro_factory, interval_seconds, name)
```

Recurring background coroutines launched by `MachinaCore`:

| Name | Interval | Purpose |
|------|----------|---------|
| `approval_sweeper` | 30s | Expire overdue approval requests |
| `demo_sweeper` | 60s | Expire stale demo sessions |
| `health_sweeper` | 60s | Auto-heal DEGRADED/OFFLINE agents |
| `capability_sweeper` | 90s | Discover capabilities for all agents |
| `broadcast_sweeper` | 30s | Expire overdue broadcast queries |

### BackgroundRunner

Async task queue with configurable `max_concurrent=3`. Used for non-critical background work submitted via `POST /background/submit`.

### ServiceWatchdog

Health check registry. `run_checks()` → `healthy_services`, `degraded_services`.

---

## 21. Conversation System

**File**: `core/conversation/`

### ConversationSession

```python
class Message(BaseModel):
    role: str     # "user" | "assistant" | "system"
    content: str
    timestamp: datetime

class ConversationSession(BaseModel):
    session_id: str
    messages: List[Message]
    created_at: datetime
    last_active: datetime
    summary: Optional[str]    # LLM-compressed older messages
```

Multi-turn chat with SQLite persistence (`conversations.db`).

Context-aware intent parsing: `parse_intent_llm_with_context(input, history)` includes recent messages in LLM prompt for reference resolution.

Session auto-summary: when `len(messages) > threshold`, older messages are compressed via LLM and stored as `summary`. Subsequent turns include the summary instead of full history.

`purge_stale(max_age_days, min_messages)` — removes old/empty sessions.

---

## 22. GitHub Integration

**File**: `integrations/github/`

7 tools registered under `github.*` namespace. All tools use a PAT stored in preferences (separate from LLM config).

### Tool Schemas

| Tool | Parameters | Notes |
|------|-----------|-------|
| `github.list_repos` | `type`, `sort`, `limit` | type: owner/all/public/private |
| `github.repo_info` | `owner`, `repo` | Returns full metadata |
| `github.list_branches` | `owner`, `repo`, `limit` | Includes protected flag |
| `github.list_issues` | `owner`, `repo`, `state`, `limit` | state: open/closed/all |
| `github.list_prs` | `owner`, `repo`, `state`, `limit` | Includes draft flag |
| `github.create_issue` | `owner`, `repo`, `title`, `body`, `labels` | HIGH risk, requires approval |
| `github.clone` | `owner`, `repo`, `path` | Authenticated HTTPS, HIGH risk |

Intent routing detects patterns like `"list my github repos"`, `"show github issues for owner/repo"`, and maps to `github_command` intent without LLM.

---

## 23. Demo Mode

**File**: `core/demo/`

### Tier System

```python
class DemoMode(str, Enum):
    INTERNAL = "internal"    # full access
    REVIEWER = "reviewer"    # write but non-destructive
    DEMO = "demo"            # read-only
```

### Tool Gating

`ToolRegistry.set_allowed_tools(allowed_set)`:
- `DEMO_SAFE_TOOLS` (17): read-only tools only
- `REVIEWER_EXTRA_TOOLS` (14): adds write-but-safe tools
- `BLOCKED_TOOLS` (6): always blocked in non-internal modes (`process.stop`, `shell.run`, etc.)
- `is_tool_gated(tool_name) -> bool`
- Blocked invocations return `DEMO_TOOL_BLOCKED` error code

### Output Sanitization

`sanitize_output(output)` strips:
- Home directory paths (`/home/user`, `C:\Users\Name`)
- Usernames from paths
- Windows drive letters from absolute paths

Wired into `_plan_to_response()` automatically.

### DemoSessionManager

TTL-based session lifecycle (default 30 min):
- `create_session()` → returns session_id
- `get_session(id)` → touches TTL
- `expire_stale()` → called by 60s sweeper

### Reviewer Authentication

HMAC-SHA256 token generation/verification via `MACHINA_REVIEWER_SECRET` env var.

---

## 24. Workspace Intelligence

**File**: `core/workspace/`

### Workspace Model

```python
class Workspace(BaseModel):
    workspace_id: str
    path: str
    name: str
    languages: List[str]       # detected by file extension
    frameworks: List[str]      # detected by marker files (package.json → Node, etc.)
    key_files: List[str]       # README, entry points, configs
    has_git: bool
    last_indexed: datetime
```

### Framework Detection

Marker file mappings:
- `package.json` → Node.js
- `pyproject.toml` / `setup.py` / `requirements.txt` → Python
- `Cargo.toml` → Rust
- `pom.xml` → Java/Maven
- `docker-compose.yml` → Docker
- `.github/` → GitHub Actions

Auto-indexing: `run()` indexes workspace on first encounter, caches in memory + SQLite (`workspaces.db`).

Workspace context is injected into:
- LLM planner system prompt (languages, frameworks)
- Conversational chat system prompt

---

## 25. Desktop Shell (Tauri 2)

**File**: `desktop/`

### Architecture

- Frameless Tauri 2 window wrapping the web UI in an iframe
- Rust backend lifecycle: spawns Python FastAPI as child process, detects existing backend on port 8100
- Health polling: raw TCP health check bypasses CORS; navigates webview on success
- Loading screen: glassmorphic splash → iframe transition (persistent shell architecture, no page navigation after connect)

### Embedded Python Distribution

- `scripts/bundle_python.py --with-rag` downloads CPython 3.12 embeddable + pip + all deps including ChromaDB
- Bundle location: `desktop/src-tauri/bundle/python/`
- Installer size: ~125 MB MSI (zero prerequisites on target)
- `find_embedded_python()` in Rust: checks `bundle/python/python.exe` first (distribution), falls back to system `python` (dev)

### Auto-Updater

- `tauri-plugin-updater v2` with background check (10s after UI load)
- Checks GitHub Releases endpoint for `latest.json`
- Glassmorphic notification banner with **Install & Restart** / **Later** buttons
- `scripts/generate_update_manifest.py`: post-build job generates `latest.json` with per-platform signatures

### System Tray

- Show/Quit menu; left-click to focus
- Close-to-tray: window hides instead of quitting

---

## 26. API Reference Summary

### Core Task Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/run` | Execute a natural-language command |
| POST | `/chat` | Multi-turn conversational message |
| GET | `/chat/stream` | Server-sent events streaming |
| POST | `/tasks` | Create task directly |
| GET | `/tasks/{id}` | Get task details |
| POST | `/tasks/{id}/resume` | Resume paused task |
| POST | `/tasks/{id}/pause` | Pause executing task |
| POST | `/tasks/{id}/abort` | Abort task |
| POST | `/tasks/{id}/retry/{step_id}` | Retry a failed step |
| GET | `/approvals` | List pending approvals |
| POST | `/approvals/{id}/approve` | Grant approval |
| POST | `/approvals/{id}/deny` | Deny approval |
| GET | `/runtime/status` | Runtime snapshot |

### Agent Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET/POST | `/agents` | List / create agents |
| GET/PUT/DELETE | `/agents/{id}` | Read / update / delete agent |
| GET | `/agents/summary` | Fleet health summary |
| GET/PUT | `/orchestration` | Get / set orchestration config |
| GET | `/agents/delegation-chains` | Active delegation chains |
| GET/DELETE | `/agents/{id}/memory` | Agent memory CRUD |
| GET | `/agents/{id}/capabilities` | Capability scores |
| GET | `/agents/{id}/capabilities/discovered` | Discovered capabilities |
| GET | `/agents/{id}/reputation` | Reputation metrics |
| GET | `/agents/{id}/health` | Health record |
| POST | `/agents/{id}/health/status` | Manual status override |
| POST | `/agents/{id}/auto-heal` | Trigger auto-heal |
| GET | `/agents/{id}/health/history` | Health check log |
| GET | `/agents/{id}/health/trends` | Performance trends |
| GET | `/agents/{id}/performance` | Combined performance view |
| GET | `/agents/performance/comparison` | All agents comparison |
| GET | `/agents/communications/feed` | Unified communication timeline |
| GET | `/agents/communications/graph` | Communication graph nodes/edges |
| GET | `/agents/health` | All agents health |

### Workflow Chain Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET/POST | `/workflow-chains` | List / create chains |
| GET/PUT/DELETE | `/workflow-chains/{id}` | Read / update (versioned) / delete |
| POST | `/workflow-chains/{id}/execute` | Sequential execution |
| POST | `/workflow-chains/{id}/execute-parallel` | Parallel group execution |
| POST | `/workflow-chains/{id}/negotiate` | Pipeline capability negotiation |
| POST | `/workflow-chains/{id}/optimize` | Dependency analysis |
| POST | `/workflow-chains/{id}/apply-optimization` | Apply parallel groups |
| POST | `/workflow-chains/{id}/auto-assign` | Best-agent assignment |
| POST | `/workflow-chains/{id}/rollback` | Rollback to version |
| GET | `/workflow-chains/{id}/versions` | Version history |
| POST | `/workflow-chains/{id}/resolve-conflicts` | Resolve negotiation ties |
| POST | `/workflow-chains/negotiate-all` | Bulk negotiation |
| POST | `/workflow-chains/from-template/{id}` | Create from template |
| GET | `/workflow-chain-templates` | List built-in templates |

---

## 27. Data Flow: End-to-End Example

User input: `"grep for TODO in the src directory"`

```
1. Intake
   text → _heuristic_route() → intent="grep" (keyword match)
   entities={"pattern": "TODO", "path": "src"}

2. Planner
   _plan_grep() → Plan with 1 step:
     { tool: "filesystem.grep", arguments: {pattern: "TODO", path: "src"} }

3. Validator
   check tool exists ✓, required params present ✓, no HIGH risk ✓
   validation_status = VALID

4. TaskRuntime
   create_task() → Task(status=CREATED)
   transition: CREATED → INTAKE_COMPLETE → PLANNED → VALIDATED → READY

5. StepRuntime
   register_steps() → step record in SQLite
   prime_steps(): policy=LOW → ALLOW → step status=READY

6. RuntimeExecutor
   run_step():
     - no delegate_to
     - no consensus patterns
     - invoke("filesystem.grep", {pattern:"TODO", path:"src"})

7. ToolRegistry
   timeout enforced (120s)
   filesystem.grep handler runs subprocess grep
   returns ToolResult{output: [{file, line, match}, ...], error_code: None}

8. StepRuntime
   transition step: RUNNING → SUCCEEDED
   _sync_task_status() → task EXECUTING → COMPLETED

9. EventBus
   emits: tool_started, tool_finished, task_completed
   persisted to SQLite + JSONL

10. MachinaCore
    _format_dict_output() → human-readable summary
    response served to client
```

---

## 28. Test Infrastructure

**File**: `tests/`

2148 tests across 50+ test modules.

### Key Test Modules

| Module | Focus | Tests |
|--------|-------|-------|
| `test_executor_flow.py` | End-to-end runtime (task→steps→execute→events→snapshot) | 12 |
| `test_approval_flow.py` | Approval lifecycle (grant/deny/sync) | 8 |
| `test_state_transitions.py` | Task/Step/Approval FSM through runtime coordinators | 43 |
| `test_agents.py` | Agent CRUD, pool, bus, delegation schema | 53+ |
| `test_agent_persistence.py` | Store, pool lifecycle events, delegation chains | 38 |
| `test_sprint21.py` | Negotiation, capability scoring, consensus executor | 58 |
| `test_sprint22.py` | Reputation, patterns, handoffs, auto-counter | 69 |
| `test_sprint23.py` | Health, chains, discovery, performance | 49 |
| `test_sprint24.py` | HealthStore, chain execution, health-aware routing | 38 |
| `test_sprint25–31.py` | Branching, conditions, bridging, parallel chains, scheduling | ~150 |

### Test Configuration

`tests/conftest.py`: `sys.path` setup ensuring project root is importable regardless of invocation.

`MachinaCore.close()` calls `clear_intake_state()` which resets module-level `_tool_registry_names` and `_workflow_store_ref` — preventing stale SQLite refs from cross-test contamination.

Run the full suite:
```bash
python -m pytest tests/ -x -q
```

---

## 29. Configuration & Environment

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MACHINA_LLM_PROVIDER` | `ollama` | LLM provider selection |
| `MACHINA_LLM_URL` | `http://localhost:11434` | LLM base URL |
| `MACHINA_LLM_MODEL` | `llama3` | Default model |
| `MACHINA_LLM_API_KEY` | — | API key for cloud providers |
| `MACHINA_MODE` | `internal` | Demo mode tier |
| `MACHINA_REVIEWER_SECRET` | — | HMAC secret for reviewer auth |

### Preferences (Persisted)

All user configurations are stored in the `preferences` memory scope:
- `llm_provider`, `llm_url`, `llm_model`, `llm_api_key`
- `github_token`
- `personality_profile`
- `demo_mode`
- `workspace_root`

Restored on `MachinaCore` startup.

### SQLite Databases

| File | Contents |
|------|----------|
| `events.db` | Event log (canonical envelope) |
| `memory.db` | Task history + layered memory scopes |
| `telemetry.db` | Plan/tool metrics |
| `conversations.db` | Chat session history |
| `workspaces.db` | Indexed workspace records |
| `workflows.db` | User-defined workflow definitions |
| `agents.db` | User-created agent definitions |
| `health.db` | Agent health checks, snapshots, trends |

WAL auto-cleanup on startup: `_cleanup_stale_wal()` removes orphaned `.db-wal` and `.db-shm` files.

---

## 30. Security Posture Summary

| Layer | Mechanism |
|-------|-----------|
| Tool execution | Risk-level policy gating; approval required for HIGH |
| Filesystem | Path safety: reads allowed in system dirs, writes workspace-bounded |
| Shell | Privilege escalation blocking (sudo/runas); destructive command detection |
| Secrets | AES-256-GCM encryption (600k PBKDF2 iterations) |
| Output | CredentialScrubber (20+ patterns) auto-applied to all plan responses |
| Audit | SHA-256 hash chain on every audit log entry |
| Agent ops | Delegation cycle detection; depth limiting (max 5) |
| Demo mode | Tool whitelist enforcement; output sanitization |
| GitHub | PAT stored in preferences; only used for github.* tools |
| MCP | MEDIUM risk by default; sandboxed under `mcp.<server>.<tool>` namespace |
