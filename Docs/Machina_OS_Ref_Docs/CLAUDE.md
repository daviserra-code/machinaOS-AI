# CLAUDE.md

## Project
**Machina OS** — an AI-native operating environment built in iterative layers, starting from a local agentic desktop orchestrator and evolving toward a deeply integrated operating shell.

## Mission
Machina OS should behave like an operating system that understands user intent, plans actions, invokes tools, manages memory, and executes workflows safely on the local machine.

The first goal is **not** to build a real kernel.  
The first goal is to build a **credible AI-native operating layer** on top of an existing OS.

---

## Product Vision
Machina OS is an **intent-driven system**.

Instead of forcing the user to manually open tools and coordinate steps, Machina OS should:
- understand goals
- decompose them into tasks
- choose tools
- execute steps
- ask for confirmation only when risk is non-trivial
- keep track of context, preferences, and outcomes

Example:
> “Prepare my development environment for Project X.”

Expected behavior:
1. Locate the repo
2. Open the workspace
3. Start required services
4. Restore recent context
5. Present a concise status summary

---

## Current Development Strategy
Build Machina OS in 3 stages.

### Stage 1 — Machina Core
A local agent orchestrator that can:
- receive natural-language commands
- plan tasks
- call tools
- maintain short-term memory
- log actions
- run on top of Windows/Linux/macOS

### Stage 2 — Machina Shell
A system shell / workspace interface with:
- command palette
- conversational task execution
- file and process awareness
- permission-aware automation
- visual task timeline

### Stage 3 — Machina OS Layer
Deeper integration with:
- background services
- policy engine
- semantic filesystem features
- persistent memory
- multi-agent coordination
- optional custom desktop environment

---

## Non-Goals
For the MVP, do **not** attempt:
- custom kernel development
- custom drivers
- full desktop environment replacement
- uncontrolled autonomous behavior
- broad cloud dependency
- “general intelligence” claims

Stay brutally practical.

---

## Engineering Principles
1. **Local-first where possible**  
   User files, task state, memory, and orchestration should run locally by default.

2. **Explicit tool boundaries**  
   The model must never “pretend” to perform an action.  
   Every action must map to a real tool invocation.

3. **Human approval for risky actions**  
   Destructive file ops, command execution, network actions, credential use, and process killing require policy checks.

4. **Deterministic logs**  
   Every meaningful action must be logged in a structured way.

5. **Planner / executor separation**  
   Planning and execution should be distinct modules.

6. **Composable memory**  
   Memory should be layered: session, episodic, semantic, preferences.

7. **Graceful degradation**  
   If the model is unavailable, the system should still expose logs, state, tools, and recoverable workflows.

8. **No fake magic**  
   Avoid vague AI theater. Build inspectable behavior.

9. **Reversibility**  
   Mutations should be reversible. File writes back up originals. Git operations expose diff previews. Rollback should be possible.

---

## Technical Stack (Actual)

### Backend
- Python 3.14+
- FastAPI for local APIs (port 8100)
- Pydantic for schemas
- Uvicorn for local service runtime
- httpx for async HTTP to LLM providers

### Agent / Orchestration
- Custom planner → executor pipeline (no LangGraph)
- Unified runtime stack: contracts → guards → emitter → runtime store → TaskRuntime → StepRuntime → RuntimeExecutor
- Heuristic-first intent routing: run(), chat(), chat_stream() prefer heuristic parser for deterministic intents before LLM fallback
- Dynamic tool-name routing: registry-populated _tool_registry_names set enables dot-notation detection (system.info, filesystem.list, etc.) with prefix-to-intent mapping and filesystem sub-intent refinement
- LLM intent guardrail: _query_has_tool_signal() last-resort check prevents LLM from hijacking queries containing registered tool names
- Human-readable output formatting: _format_system_output() for system tools, _format_dict_output() for generic dicts
- Hybrid planning: deterministic templates for known intents, LLM for open-ended
- Deterministic intents: list, read_file, write_file, delete_file, run_command, git_command, list_processes, analyze_repository, dev_workflow, system_info, grep, create_project, cleanup, find_and_read, semantic_search, workflow, refactor, debug_issue, delegate
- Plan validator: schema enforcement, step limits (12 max), auto-fix
- Tool registry with typed schemas, risk levels, output schemas, and execution limits
- Tool Protocol compliance: structured error codes, path safety, privilege escalation blocking
- LLM-assisted intake parsing + plan generation
- Path normalization: 'current directory' and similar phrases auto-resolved to '.'
- Dual LLM provider support: Ollama (default) and OpenAI-compatible (Groq, etc.)
- Environment variables: `MACHINA_LLM_PROVIDER`, `MACHINA_LLM_URL`, `MACHINA_LLM_MODEL`, `MACHINA_LLM_API_KEY`

### Multi-Agent Coordination
- AgentDefinition: capability profile with name, description, capabilities, tool_filter (fnmatch globs), system_prompt, enabled flag
- BUILTIN_AGENTS: filesystem (filesystem.*), git (git.*), shell (shell.*/process.*), system (system.*)
- AgentPool: register/unregister/find agents by capability, intent, or tool name; strategy-aware selection
- AgentBus: inter-agent pub/sub messaging with send, broadcast, subscribe (by agent/type/all), capped history
- AgentMessage: Pydantic model with source_agent, target_agent, message_type, payload, correlation_id, task_id
- PlanStep.delegate_to: optional agent_id for scoped tool execution
- RuntimeExecutor delegation check: AGENT_TOOL_DENIED error if agent rejects tool, delegation events on agent bus
- RuntimeExecutor fallback delegation: when FALLBACK strategy active, tries candidates_for_tool() before failing
- RuntimeExecutor pipeline execution: run_pipeline() chains agents sequentially with output passing
- Intake detection: "delegate to", "ask agent", "use agent", "send to agent" patterns
- Planner: deterministic _plan_delegate() with agent pool resolution, routes to agent-specific tools
- Planner: decompose_for_agents() decomposes complex intents into agent-scoped sub-plans
- Agent-aware LLM planner: agent catalog injected into system prompt, delegate_to parsed from LLM output
- Agent-aware chat prompts: available agents listed in conversational system prompts

### Agent Persistence
- AgentStore: SQLite-backed CRUD persistence (agents.db) for user-created agents
- AgentPool store integration: register/unregister auto-persist non-builtin agents, load persisted agents on init
- Builtin isolation: _builtin_ids set prevents builtin agents from being written to store
- DelegationChain: cycle detection and depth limiting (max_depth=5) for agent-to-agent delegation
- AgentBus.delegate(): validated delegation with cycle/depth checks before sending delegation_request messages
- RuntimeExecutor chain validation: creates/validates DelegationChain per step, DELEGATION_CYCLE error on violation

### Consensus Decision Making
- ConsensusStrategy(str, Enum): MAJORITY, UNANIMOUS, WEIGHTED
- VoteValue(str, Enum): APPROVE, REJECT, ABSTAIN
- ConsensusStatus(str, Enum): PENDING, RESOLVED, REJECTED, EXPIRED
- ConsensusRequest model: question, candidates, votes, strategy, min_voters, resolution logic
- Vote model: agent_id, value, weight, reason, cast_at
- AgentBus.request_consensus(): create consensus request, notify candidates via bus
- AgentBus.cast_vote(): record agent votes with weight and reason, emit consensus_vote events
- AgentBus.resolve_consensus(): evaluate votes per strategy, emit consensus_resolved events
- OrchestrationConfig: consensus_strategy and consensus_min_voters fields
- API: POST /consensus, GET /consensus, GET /consensus/{id}, POST /consensus/{id}/vote, POST /consensus/{id}/resolve
- UI: Consensus panel in Agents view with create form, vote buttons, resolve controls

### Agent Memory Scoping
- MemoryStore 'agent' scope: per-agent namespaced memory partitions (agent_id:key pattern)
- set_agent_memory(), get_agent_memory(), delete_agent_memory(), list_agent_keys(), clear_agent_memory()
- Agent memory isolation: different agents' memory independent, clearing one doesn't affect others
- API: GET/PUT/DELETE /agents/{id}/memory, DELETE /agents/{id}/memory (clear all)
- UI: Agent Memory section with agent selector, key-value viewer, delete controls

### Delegation Chain Visualization
- API: GET /agents/delegation-chains returns active chain paths, depth, max_depth
- UI: Delegation Chains section showing chain paths with agent flow arrows, depth indicators

### Agent-to-Agent Negotiation
- NegotiationPhase(str, Enum): PROPOSED, COUNTERED, ACCEPTED, REJECTED, RESOLVED, FAILED, WITHDRAWN
- NegotiationPriority(int, Enum): CRITICAL=1, HIGH=2, NORMAL=3, LOW=4
- NegotiationProposal model: initiator, responder, tool, step_id, task_id, phase, priority, reason, counter_reason, proposed_agent, counter_agent, max_rounds (1-10, default 3), current_round, winner
- Proposal lifecycle: propose() → counter() (multi-round) → accept()/reject()/withdraw(), resolve_by_priority() (lower priority value wins, tie→initiator)
- is_terminal property: True for ACCEPTED, REJECTED, RESOLVED, FAILED, WITHDRAWN
- AgentBus negotiation methods: start_negotiation, counter_negotiation, accept_negotiation, reject_negotiation, resolve_negotiation_by_priority, get_negotiation, list_negotiations
- Negotiation events: negotiation_proposed, negotiation_countered, negotiation_accepted, negotiation_rejected, negotiation_resolved emitted on agent bus
- API: POST/GET /negotiations, GET /negotiations/{id}, POST /negotiations/{id}/counter, /accept, /reject, /resolve
- UI: Negotiations panel with create form, priority selector, counter/accept/reject/auto-resolve buttons, phase-colored badges

### Consensus-Aware Executor
- RuntimeExecutor.consensus_tool_patterns: fnmatch glob patterns identifying tools requiring multi-agent consensus
- RuntimeExecutor.run_step_with_consensus(): gates tool execution on consensus when tool matches patterns and >=2 candidate agents exist
- Auto-voting: each candidate agent votes based on capability confidence (>=0.3 → APPROVE weighted by confidence, <0.3 → REJECT weighted by 1-confidence)
- Consensus resolution: RESOLVED → proceed with run_step(), REJECTED → CONSENSUS_REJECTED error code
- Fallback: skips consensus when no patterns configured, single agent, or no bus/pool

### Capability Learning
- CapabilityScore model: agent_id, tool, successes, failures, total_duration_ms, last_error_code, error_counts dict
- record_success(duration_ms), record_failure(error_code, duration_ms) methods
- Confidence formula: success_rate * min(1.0, sample_size / 20), neutral prior 0.5 when no data
- RuntimeExecutor._record_capability(): persists CapabilityScore to agent memory after each tool execution
- RuntimeExecutor._get_capability_confidence(): retrieves confidence from memory store
- RuntimeExecutor.get_agent_capabilities(): returns all capability scores for an agent
- API: GET /agents/{agent_id}/capabilities
- UI: Capability Learning panel with agent selector, table showing tool/success_rate/confidence/avg_duration/samples/last_error

### Agent Reputation
- AgentReputation model: agent_id, total_successes, total_failures, total_tasks, total_duration_ms, tools_used dict (tool→count), recent_outcomes list (last 50)
- Properties: sample_size, success_rate, recent_success_rate (recent window only), reputation_score (weighted blend: 40% lifetime + 60% recent × sample_confidence)
- record(tool, success, duration_ms), record_task() methods
- RuntimeExecutor._record_capability() also records AgentReputation to agent memory after each delegated tool execution
- RuntimeExecutor.get_agent_reputation(): returns cross-task reputation dict (score, rates, tools_used, sample_size)
- API: GET /agents/{agent_id}/reputation
- UI: Agent Reputation panel with agent selector, reputation/success cards, tools used badges

### Consensus Pattern Learning
- ConsensusPatternScore model: pattern, approvals, rejections, updated_at
- Properties: total, approval_rate, should_skip_consensus (True if total >= 10 and approval_rate > 0.95)
- record_outcome(approved) method
- AgentBus: record_consensus_outcome(), get_consensus_pattern(), list_consensus_patterns(), should_skip_consensus()
- RuntimeExecutor.run_step_with_consensus(): dynamic skip when pattern has high enough approval rate
- RuntimeExecutor: records consensus outcome after resolution for pattern learning
- API: GET /consensus/patterns, GET /consensus/patterns/{tool}
- UI: Consensus Patterns table with tool pattern, approvals/rejections, approval rate, auto-skip indicator

### Negotiation Auto-Counter
- suggest_counter_agents(): ranks alternative agents by capability confidence, excludes proposed agent
- AgentBus.auto_counter(): picks best alternative via suggest_counter_agents(), submits counter-proposal, broadcasts negotiation_auto_countered event
- API: POST /negotiations/{negotiation_id}/auto-counter
- UI: Auto-Counter button on active negotiation cards

### Task Handoff Protocol
- HandoffStatus(str, Enum): REQUESTED, ACCEPTED, DECLINED, EXECUTING, COMPLETED, FAILED, CANCELLED
- HandoffRequest model: handoff_id (auto "ho_" prefix), from_agent, to_agent, tool, step_id, task_id, status, preconditions (list), constraints (dict), reason, decline_reason, created_at, resolved_at
- Lifecycle methods: accept(), decline(reason), start_execution(), complete(), fail(reason), cancel()
- is_terminal property: True for DECLINED, COMPLETED, FAILED, CANCELLED
- AgentBus: request_handoff, accept_handoff, decline_handoff, complete_handoff, fail_handoff, cancel_handoff, get_handoff, list_handoffs (with agent_id/task_id/active_only filters)
- Events: handoff_requested, handoff_accepted, handoff_declined, handoff_completed, handoff_failed, handoff_cancelled
- API: POST/GET /handoffs, GET /handoffs/{id}, POST /handoffs/{id}/accept, /decline, /complete, /cancel
- UI: Handoffs panel with create form, status cards, accept/decline/complete/cancel buttons

### Agent Health Monitoring
- AgentHealthStatus(str, Enum): ONLINE, DEGRADED, OFFLINE
- AgentHealthRecord model: agent_id, status, consecutive_failures/successes, total_checks, avg_latency_ms, recent_latencies (rolling window), last_error, degraded_since, offline_since
- record_check(): update health metrics and auto-evaluate status (error streak → DEGRADED → OFFLINE, recovery → ONLINE)
- Latency degradation detection: recent latency > baseline × factor triggers DEGRADED
- AgentBus: record_health_check, get_agent_health, list_agent_health, set_agent_status (manual override)
- Events: agent_health_changed (emitted on status transitions)
- API: GET /agents/health, GET /agents/{id}/health, POST /agents/{id}/health/status

### Agent Health Persistence
- HealthStore: SQLite-backed (health.db) persistence with three tables: health_checks, health_snapshots, performance_trends
- health_checks table: individual check events (agent_id, success, latency_ms, error, error_code, recorded_at)
- health_snapshots table: periodic full-record snapshots (status, consecutive_failures/successes, total_checks, avg_latency_ms, snapshot_data JSON)
- performance_trends table: time-series trend data (reputation_score, success_rate, avg_latency_ms, total_tasks, total_successes, total_failures, health_status)
- AgentBus auto-persist: record_health_check() writes to health_checks + saves snapshot after each update
- Snapshot restoration: _load_health_snapshots() restores last-known AgentHealthRecord per agent on startup
- AgentBus: record_performance_trend(), get_health_checks(), get_health_trends()
- API: GET /agents/{id}/health/history, GET /agents/{id}/health/trends

### Agent Workflow Chains
- AgentWorkflowStep model: agent_id, tool, arguments, description, output_key, input_from, condition, branch_to, parallel_group
- AgentWorkflowStep.condition: optional condition string (format: `output_key:field op value`, ops: `==`, `!=`, `contains`, `not_empty`)
- AgentWorkflowStep.branch_to: optional agent_id for cross-agent branching when condition fails (re-routes instead of skipping)
- AgentWorkflowStep.parallel_group: optional group key — steps sharing the same non-empty parallel_group run concurrently via asyncio.gather
- AgentWorkflowChain model: chain_id, name, description, steps list, agent_sequence property, version, version_history, updated_at
- AgentWorkflowChain.snapshot(): serialisable state capture with version, name, steps, timestamp
- AgentWorkflowChain.update_steps(new_steps, description): saves current state to version_history, increments version, replaces steps
- AgentWorkflowChain.rollback(target_version): reverts to historical state (saves current first), returns True on success
- AgentBus: create_workflow_chain, get_workflow_chain, list_workflow_chains, delete_workflow_chain, update_workflow_chain, rollback_workflow_chain
- AgentBus.optimize_chain(): dependency graph analysis via output_key/input_from, topological grouping into parallel execution groups
- AgentBus.apply_optimization(): applies optimize_chain() results as parallel_group annotations on chain steps
- AgentBus.auto_assign_chain(): uses negotiate_pipeline to assign best agents to chain steps by capability confidence
- Events: workflow_chain_created, workflow_chain_deleted, workflow_chain_updated, workflow_chain_rolled_back
- RuntimeExecutor.run_workflow_chain(): converts chain steps to PlanSteps, registers with StepRuntime, executes sequentially with output bridging, condition evaluation, and cross-agent branching, stops on failure
- RuntimeExecutor.run_workflow_chain_parallel(): groups steps by parallel_group, runs groups sequentially but concurrent within group via asyncio.gather, falls back to sequential when no groups
- RuntimeExecutor.schedule_task(): auto-routes task to best agent via AgentPool.best_agent_for_tool(), enqueues on bus, returns {status, agent_id, item_id, confidence}
- RuntimeExecutor.evaluate_condition(): parses `output_key:field op value` against collected step outputs, supports `==`, `!=`, `contains`, `not_empty`
- Conditional step gating: steps with unmet conditions are skipped via skip_step() with SKIPPED status, or re-routed via branch_to
- Cross-agent branching: when condition fails and branch_to is set, step.delegate_to is re-routed to alternate agent instead of skipping
- Enhanced output bridging: _bridge_step_input() injects `_prior_output` key, resolves path from files/matches/string/list, forwards non-underscore dict keys via setdefault
- BUILTIN_CHAIN_TEMPLATES: pre-built reusable chain definitions (code-review, deploy-check, project-scan)
- AgentBus.create_chain_from_template(): instantiates AgentWorkflowChain from built-in template by name
- API: POST/GET /workflow-chains, GET/DELETE /workflow-chains/{id}, POST /workflow-chains/{id}/execute, PUT /workflow-chains/{id} (versioned update), POST /workflow-chains/{id}/rollback, GET /workflow-chains/{id}/versions, POST /workflow-chains/from-template/{template_id}, GET /workflow-chain-templates, POST /workflow-chains/{id}/negotiate, POST /workflow-chains/{id}/auto-assign, POST /workflow-chains/{id}/optimize, POST /workflow-chains/{id}/apply-optimization
- UI: Workflow Chains panel with drag-and-drop step editor (description, output_key, input_from, arguments JSON, condition, branch_to, parallel_group fields per step), vertical flow visualization with colored badges, Optimize/Auto-Assign/Negotiate/Execute/Parallel/Rollback/History buttons, template picker

### Agent Broadcast Queries
- BroadcastQueryStatus(str, Enum): PENDING, COLLECTING, COMPLETED, EXPIRED
- BroadcastQuery model: query_id (auto "bq_" prefix), from_agent, question, target_agents list, responses dict, status, created_at, completed_at, is_complete property
- BroadcastQuery lifecycle: add_response(agent_id, payload), complete()
- AgentBus: broadcast_query(), respond_to_query(), complete_query(), get_query(), list_queries() (with active_only filter)
- Events: broadcast_query, broadcast_query_response, broadcast_query_completed
- API: POST/GET /broadcast-queries, GET /broadcast-queries/{id}, POST /broadcast-queries/{id}/respond, POST /broadcast-queries/{id}/complete
- UI: Broadcast Queries panel with form, query list, status colors, Complete button

### Capability Announcements
- CapabilityAnnouncement model: announcement_id (auto "cann_" prefix), agent_id, capabilities list, tool_filter list, announced_at
- AgentBus: announce_capabilities(), list_announcements() (with agent_id filter)
- Events: capability_announced
- API: POST/GET /capability-announcements
- UI: Capability Announcements panel with capability/tool_filter badges

### Chain Execution History
- ChainExecutionRecord model: execution_id (auto "cex_" prefix), chain_id, chain_name, task_id, started_at, finished_at, status (RUNNING/SUCCESS/PARTIAL/FAILED), step_results list, total_steps, succeeded_steps, failed_steps, skipped_steps
- ChainExecutionRecord.finish(): computes step counters and final status from results
- AgentBus: record_chain_execution(), list_chain_executions() (with chain_id filter), get_chain_execution()
- RuntimeExecutor: run_workflow_chain() auto-records execution via bus after completion
- Events: chain_execution_recorded
- API: GET /chain-executions, GET /chain-executions/{id}
- UI: Chain Execution History panel with status colors, step counts (✓✗⊘)

### Agent Collaboration Sessions
- CollaborationSession model: session_id (auto "collab_" prefix), task_id, participants list, context dict, created_at, closed_at, is_active property
- CollaborationSession lifecycle: join(agent_id), leave(agent_id), set_context(key, value), get_context(key, default), close()
- AgentBus: create_collaboration(), join_collaboration(), leave_collaboration(), set_collaboration_context(), get_collaboration(), close_collaboration(), list_collaborations() (with active_only filter)
- Events: collaboration_created, collaboration_joined, collaboration_left, collaboration_context_updated, collaboration_closed
- API: POST/GET /collaborations, GET /collaborations/{id}, POST /collaborations/{id}/join, /leave, /context, /close
- UI: Collaboration Sessions panel with form, participant list, context key count, Close button

### Agent Request/Response Protocol
- AgentRequestStatus(str, Enum): PENDING, DELIVERED, RESPONDED, TIMEOUT, FAILED
- AgentRequest model: request_id (auto "areq_" prefix), from_agent, to_agent, action, payload, correlation_id, task_id, status, timeout_ms, created_at, delivered_at, responded_at
- AgentRequest lifecycle: deliver(), respond(), timeout(), fail(), is_terminal property
- AgentResponse model: response_id (auto "aresp_" prefix), request_id, from_agent, to_agent, success, payload, error, created_at
- AgentBus: send_request(), send_response(), get_request(), get_response_for(), list_requests() (with agent_id/active_only filters)
- Events: agent_request_sent, agent_response_sent
- API: POST/GET /agent-requests, GET /agent-requests/{id}, POST /agent-requests/{id}/respond
- UI: Agent Requests panel with from/to/action form, status-colored request list, respond button

### Pipeline Capability Negotiation
- PipelineNegotiationResult model: negotiation_id (auto "pneg_" prefix), chain_id, assignments list (step_index, tool, agent_id, confidence, source), conflicts list (step_index, tool, tied_agents, confidence), created_at
- AgentBus.negotiate_pipeline(chain, pool): scores candidates by capability confidence per step, detects ties as conflicts, returns PipelineNegotiationResult
- AgentBus._get_agent_tool_confidence(): retrieves capability confidence from memory (default 0.5)
- Events: pipeline_negotiated
- API: POST /workflow-chains/{id}/negotiate
- UI: Inline negotiation results with assignments and conflict display

### Chain Execution Replay
- ChainReplayRequest model: replay_id (auto "crep_" prefix), source_execution_id, chain_id, chain_name, override_arguments dict, result_execution_id
- AgentBus: request_chain_replay(), get_chain_replay(), list_chain_replays(), complete_chain_replay()
- RuntimeExecutor.replay_workflow_chain(): looks up source execution, re-creates chain, applies argument overrides, runs via run_workflow_chain(), links replay to result
- Events: chain_replay_requested, chain_replay_completed
- API: POST /chain-executions/{id}/replay, GET /chain-replays, GET /chain-replays/{id}
- UI: Replay button on chain execution cards

### Broadcast Response Aggregation
- AggregationStrategy(str, Enum): MERGE, FIRST, MAJORITY, ALL
- BroadcastAggregation model: aggregation_id (auto "bagg_" prefix), query_id, strategy, result, response_count
- AgentBus.aggregate_broadcast(): aggregates completed query responses per strategy (ALL=dict, FIRST=first value, MERGE=merged dict, MAJORITY=most common)
- AgentBus.expire_broadcast_query(): marks COLLECTING queries as EXPIRED with timestamp
- Events: broadcast_aggregated, broadcast_query_expired
- API: POST /broadcast-queries/{id}/aggregate, POST /broadcast-queries/{id}/expire
- UI: Aggregate button (COMPLETED/EXPIRED queries) with inline result display, Expire button (COLLECTING queries)

### Agent Task Queue
- AgentTaskStatus(str, Enum): QUEUED, RUNNING, COMPLETED, FAILED, CANCELLED
- AgentTaskItem model: item_id (auto "atq_" prefix), agent_id, tool, arguments, priority (1-5), status, result, error, is_terminal property
- AgentTaskItem lifecycle: start(), complete(result), fail(error), cancel()
- AgentBus: enqueue_task() (priority-sorted), dequeue_task() (highest priority first), complete_task_item(), fail_task_item(), cancel_task_item(), list_agent_tasks() (with active_only filter), get_task_item()
- Events: agent_task_enqueued, agent_task_dequeued, agent_task_completed, agent_task_failed, agent_task_cancelled
- API: POST/GET /agent-tasks, GET /agent-tasks/{id}, POST /agent-tasks/dequeue/{agent_id}, POST /agent-tasks/{id}/complete, /fail, /cancel
- UI: Agent Task Queue panel with enqueue form (agent/tool/priority), task list with status colors, Dequeue/Complete/Cancel buttons

### Agent Task Queue Auto-Execution
- RuntimeExecutor.auto_execute_task(item_id): dequeues task item, invokes tool via registry, completes/fails item, returns result dict
- RuntimeExecutor.auto_execute_agent_queue(agent_id): drains all QUEUED tasks for agent, executes each in priority order, returns list of results
- API: POST /agent-tasks/{id}/auto-execute, POST /agent-tasks/auto-execute-queue/{agent_id}
- UI: ⚡ Auto-Execute button on QUEUED task items, Auto-Execute All button for batch processing

### Broadcast Query Timeout
- BroadcastQuery.timeout_ms: configurable timeout in milliseconds (0 = no timeout)
- BroadcastQuery.is_overdue: property returns True when query is not terminal and elapsed time exceeds timeout_ms
- AgentBus.broadcast_query(): accepts timeout_ms keyword argument
- AgentBus.expire_overdue_queries(): sweeps all queries, expires any that are overdue, returns list of expired
- MachinaCore._broadcast_sweeper: ScheduledTask (30s interval) that calls _sweep_broadcast_timeouts()
- API: POST /broadcast-queries/with-timeout
- UI: Timeout input field on broadcast query form, timeout badge on query cards

### Agent Capability Discovery
- DiscoveredCapability model: agent_id, tool, source ("filter" or "history"), confidence, last_seen
- RuntimeExecutor.discover_capabilities(): expands tool_filter globs against registry + merges execution history from memory
- API: GET /agents/{id}/capabilities/discovered
- UI: Capability Discovery panel with agent selector, tool/source/confidence table

### Agent Performance Dashboard
- RuntimeExecutor.get_agent_performance(): combined health, reputation, capabilities, discovered capabilities, trends
- Performance trend recording: _record_capability() records time-series trend data (reputation_score, success_rate, avg_latency_ms, health_status) after each delegated execution
- API: GET /agents/{id}/performance, GET /agents/performance/comparison
- UI: Performance Dashboard comparing all agents with reputation score, success rate, latency metric cards
- UI: Performance Trends panel with agent selector, 3-card summary (Score, Success%, Latency), SVG time-series line chart (dual lines: amber=score, green=success rate)
- UI: Health History panel with agent selector, check log showing success/failure dots, latency, errors

### Agent Orchestration
- OrchestrationStrategy(str, Enum): SINGLE, ROUND_ROBIN, CAPABILITY_SCORE, FALLBACK, PIPELINE
- OrchestrationConfig(BaseModel): strategy, max_fallback_attempts (1-10, default 3), pipeline_pass_output (bool)
- score_agent_for_tool(): specificity scoring — exact match=1.0, prefix glob=0.3+specificity, open=0.1
- AgentPool.candidates_for_tool(): all matching agents sorted by specificity score, health-aware (OFFLINE excluded, DEGRADED deprioritized)
- AgentPool.select_agent(): strategy-aware selection (SINGLE/ROUND_ROBIN/CAPABILITY_SCORE/FALLBACK/PIPELINE)
- AgentPool.best_agent_for_tool(): selects agent with highest capability confidence from memory, falls back to specificity scoring
- AgentPool.agent_bus: optional AgentBus reference for health-aware routing
- MachinaCore.orchestration: property to get/set orchestration config
- API: GET/PUT /orchestration for strategy configuration
- API: GET /agents/summary (total, online, degraded, offline counts + top performer)
- AgentPool lifecycle events: agent_registered/agent_unregistered emitted on bus during register/unregister
- Auto-healing scheduler: ScheduledTask (60s interval) sweeps agent health, finds DEGRADED/OFFLINE agents, probes tool_filter patterns, triggers auto_heal()
- UI: Orchestration strategy panel in Agents view with strategy selector, fallback attempts, pipeline toggle
- UI: Agent status bar showing fleet health summary (online/degraded/offline counts + top performer)

### Memory
- SQLite (WAL mode) for events (`events.db`), task history (`memory.db`), telemetry (`telemetry.db`)
- JSONL logs for event streams (dual-write alongside SQLite)
- Explicit memory classes: session, task, project, preferences, agent — each with clear persistence rules
- File-based artifacts in `.machina/` directory

### RAG / Semantic Search
- ChromaDB (optional, local-first) for vector storage and semantic similarity search
- VectorStore wrapper with graceful degradation when chromadb is not installed
- SemanticIndexer: file chunking (800 chars, 200 overlap), content-hash deduplication, skip filters
- Explicit indexing via API endpoints (POST /rag/index) — no auto-indexing during run()
- RAG-augmented chat: relevant code snippets injected into conversational LLM context
- Lazy initialization: ChromaDB client created on first RAG access, not at startup
- Collections per workspace: `ws_<workspace_id>` with cosine similarity HNSW space

### Policy & Permissions
- Risk-level based policy engine (CRITICAL → block, HIGH → approval, MEDIUM → approval, LOW → allow)
- Capability-based permission model with scoped grants per tool
- Capability scopes: filesystem.read/write/delete, shell.execute, process.read/control, network.access, git.read/write, browser.open/search
- Configurable profiles: DEFAULT_GRANTS (all caps), READONLY_GRANTS (read-only)
- Hierarchical capabilities: granting `filesystem` covers all `filesystem.*` sub-caps

### Failure Recovery
- Error classification: transient, permanent, permission, not_found
- Configurable retry with exponential backoff for transient errors
- Partial plan recovery: plans with mixed success/failure continue to completion
- Fallback tools per step
- Rollback coordinator: steps with rollback_hint get auto-rollback on failure
- Coordinated plan rollback via `rollback_plan()` — reverses succeeded steps in order

### Telemetry
- SQLite-backed telemetry store (telemetry.db)
- Plan-level metrics: success rate, avg step count, avg duration, retry count
- Tool-level metrics: invocation count, success rate, avg/min/max latency, error class
- API endpoints: `/metrics`, `/metrics/errors`

### Conversation
- Multi-turn conversation sessions with SQLite persistence (conversations.db)
- Context-aware intent parsing and plan generation (conversation history injected)
- Session auto-summary: older messages compressed via LLM when turn count exceeds threshold
- Conversational vs task routing: greetings/questions handled without tool execution
- Stale session cleanup: purge_stale(max_age_days, min_messages) removes old/empty sessions

### LLM Routing
- Multi-LLM router with capability-based routing (general, fast, planning, conversation, coding)
- Priority-ordered fallback: if preferred provider fails, next route is tried automatically
- Routes support chat, chat_stream, and generate operations

### UI
- Tailwind CSS single-page app served from FastAPI static files
- Glassmorphic "stitch" design with 12 views: Home, Chat, Tools, Memory, Workflows, Agents, Timeline, Explorer, Processes, Metrics, Events, Settings
- SSE streaming for real-time event updates + WebSocket for live event push
- Approval prompts via `/approve/{plan_id}/{step_index}` API
- Multi-turn conversational chat with streaming token display
- Memory browser: scopes, preferences, workspaces, sessions
- Workflow composer: visual CRUD for user-defined multi-step workflows
- Notification system: toast popups + bell badge + notification panel
- Agent manager: CRUD for custom agents, capability/tool_filter editing, agent message log
- Keyboard UX: Enter to send, Escape to clear, Up/Down arrow for input history, Ctrl+L to focus chat, Ctrl+1-9 for view switching, Alt+N for new chat
- Command Palette: Ctrl+K fuzzy search across views, tools, quick actions; keyboard navigation (arrows, Enter, Escape); unmatched queries sent to chat
- File Explorer: directory browsing with breadcrumb navigation, go-up, file preview (100KB cap), file-type icons
- Process Monitor: sortable table (PID, Name, Status, CPU%, Memory), search filter, stop process with confirmation
- System Status Bar: persistent bottom bar showing workspace hostname, active tasks, agent fleet status, memory usage (30s polling)
- Smart suggestions: context-aware follow-up actions after task completion
- Error explanation: LLM-powered error analysis with inline explain buttons on failed steps
- Rollback/retry UI: inline retry and explain buttons on failed plan steps
- Pipeline wizard: drag-and-drop workflow chain step editor with agent/tool dropdowns (populated from API), description/output_key/input_from/arguments/condition/branch_to/parallel_group fields, HTML5 drag reordering, auto-assign agents button, vertical flow visualization with colored badges

### Workspace Intelligence
- Workspace model with language/framework detection, key file discovery
- Directory indexing: walks tree, detects languages by extension, frameworks by marker files
- Workspace auto-indexing: run() auto-indexes workspace on first encounter, caches in memory + SQLite
- Workspace context in LLM planner: detected languages/frameworks injected into planner system prompt
- Workspace context in chat: conversational replies include workspace languages, frameworks, key files
- Workspace persistence via SQLite (workspaces.db)
- Preferences engine: typed preferences with defaults, backed by MemoryStore

### Agent Personality
- PersonalityProfile model: tone, verbosity, emoji, greeting, custom system_instructions
- Personality-aware system prompts: profile fragment injected into all LLM conversational calls
- 4 built-in presets: default (professional), casual, minimal, detailed
- Persistence via PreferencesEngine (survives restarts)
- UI personality tab: preset selector, individual field controls, custom instructions editor
- API: GET/PUT /personality, GET /personality/presets, PUT /personality/preset/{name}

### Workflow Composition DSL
- WorkflowDefinition model: named, reusable multi-step workflow chains with trigger patterns
- WorkflowStep: mirrors PlanStep shape (tool, arguments, output_key, input_from, fallback, timeout, rollback_hint)
- Variable substitution: `{{var}}` placeholders in step arguments resolved at runtime from entities/bindings
- Trigger matching: case-insensitive substring matching against user input
- WorkflowStore: SQLite-backed CRUD persistence (workflows.db) with enabled/disabled toggle
- Planner integration: user workflows checked before `_plan_general` fallback, produces workflow-v1 plans
- Intake detection: "run workflow X", "execute workflow X", "workflow X" heuristic parsing
- Compound expansion: refactor (tree→git→diagnostics→diff→summary) and debug_issue (diagnostics→git→grep→summary) templates
- API: GET/POST /workflows, GET/PUT/DELETE /workflows/{id}
- UI: Workflow Composer view with visual step editor, trigger/variable configuration, enable/disable toggle

### Background Execution
- BackgroundRunner: async task queue with configurable concurrency (max_concurrent=3)
- ScheduledTask: recurring tasks with configurable intervals
- ServiceWatchdog: health check registry with degradation detection
- Agent health sweeper: ScheduledTask (60s) in MachinaCore, sweeps DEGRADED/OFFLINE agents and auto-heals via AgentBus\n- Capability discovery sweeper: ScheduledTask (90s) in MachinaCore, discovers capabilities for all agents

### Tool Protocol
- Structured error codes: every tool failure returns error_code + message (FILE_NOT_FOUND, PERMISSION_DENIED, TIMEOUT, etc.)
- Output schemas: ToolSpec includes typed output schema for every tool
- Execution limits: max execution time (120s), max output size (1 MB), hard timeout per invocation
- Path safety: filesystem tools reject system directories (Windows/POSIX), write/delete enforce workspace boundary
- Shell safety: privilege escalation blocking (sudo, runas, doas, pkexec, etc.), destructive command detection
- shell.run_safe: restricted read-only variant blocking write, delete, install, network operations

### System Integration (Implemented)
- Filesystem adapter: list, read, write, move, delete, tree, search, grep, semantic_search (9 tools with path safety)
- Filesystem reversibility: write_file backs up existing files as .machina_bak before overwriting
- Shell runner: shell.run (HIGH risk) + shell.run_safe (MEDIUM risk, read-only)
- Process manager: list, info, start, stop (OS-level, no psutil)
- Browser automation: open_url, search_files, find_recent
- Git adapter: status, log, diff, checkout, clone, branch, pull, push, commit, stash (10 tools)
- VS Code integration: open_workspace, open_file, list_extensions, install_extension, run_task, diff, read_diagnostics
- System introspection: system.status, system.info, system.memory, system.disk (4 tools, stdlib-only)
- Process visibility: GET /processes endpoint returns live OS process list

---

## Repository Structure
```text
machina-os/
  apps/
    api/              # FastAPI server, endpoints, startup
    ui/               # Tailwind SPA (index.html)
  core/
    agent/            # Top-level orchestrator (core.py), intent intake (intake.py)
    planner/          # Plan generation, validation, deterministic templates
    executor/         # Step-by-step execution with retry and failure recovery
    memory/           # SQLite-backed layered key-value store + task history
    policy/           # Risk assessment, approval engine, capability permissions
    tools/            # Tool registry with typed specs, execution limits, structured errors
    events/           # Event bus + emitter (canonical event factory)
    contracts/        # Canonical enums, prefixed IDs, runtime snapshot model
    guards/           # Task, step, approval transition guards
    runtime/          # RuntimeStore (hybrid JSONL+SQLite) + TaskRuntime + StepRuntime + RuntimeExecutor
    llm/              # LLM client with Ollama + OpenAI provider adapters + multi-LLM router
    conversation/     # ConversationSession model + SQLite store
    workspace/        # Workspace model, directory indexer, SQLite store
    telemetry/        # Execution metrics: plan/tool success rates, latency
    rag/              # ChromaDB vector store + semantic indexer (optional)
    personality/      # Agent personality profiles and response style
    workflow/         # Workflow DSL: user-defined workflow chains + SQLite store
    agents/           # Multi-agent coordination: AgentDefinition, AgentPool, AgentBus, AgentStore, DelegationChain, AgentHealthRecord, AgentWorkflowChain
    schemas.py        # Shared Pydantic models (ToolSpec, PlanStep, RiskLevel, etc.)
  integrations/
    filesystem/       # 9 filesystem tools with path safety, rollback, and semantic search
    shell/            # Shell command runner (shell.run + shell.run_safe)
    process/          # Process list/info/start/stop
    browser/          # URL opener, file search, recent files
    git/              # status, log, diff, checkout, clone, branch
    vscode/           # VS Code CLI integration (7 tools)
    system/           # System introspection (system.status, info, memory, disk)
  tests/              # 1135 pytest tests
```

---

## Core Modules

### 1. Intent Intake
Transforms raw user input into:
- intent
- entities
- constraints
- ambiguity markers
- risk level estimate

### 2. Planner
Creates an execution plan as structured steps.

A plan step should include:
- id
- description
- tool
- arguments
- requires_approval
- timeout (per-step override)
- rollback_hint (tool for undo on failure)
- expected_output
- fallback strategy

Validation enforced:
- max 15 steps per plan
- only registered tools allowed
- required params must be present
- high-risk tools force requires_approval=true
- oversized arguments truncated
- invalid fallback tools cleared
- deterministic templates for known intents bypass LLM

### 3. Executor
Runs the plan step-by-step, captures outputs, handles failures, and updates state.

Failure recovery:
- error classification (transient, permanent, permission, not_found)
- configurable retry with backoff for transient errors
- partial plan recovery — succeeding steps continue after failures
- fallback tool execution on step failure

### 4. Policy Engine
Determines whether actions:
- are safe to auto-run
- require approval
- are blocked
- need sandboxing

Capability scopes:
- `filesystem.read`, `filesystem.write`, `filesystem.delete`
- `shell.execute`
- `process.read`, `process.control`
- `network.access`
- `git.read`, `git.write`
- `browser.open`, `browser.search`

### 5. Memory
Explicit memory classes with clear persistence rules:
- session — ephemeral, cleared on reset
- task — per-task context, linked to plan_id
- project — persists across sessions
- preferences — global user settings, never auto-cleared
- agent — per-agent namespaced partitions (agent_id:key pattern)
- telemetry — system metrics (separate store)

### 6. Event Bus
Emit structured events such as:
- plan_created
- tool_started
- tool_finished
- tool_failed
- approval_requested
- task_completed

---

## Tool Design Rules
Each tool must:
- do one clear thing
- expose typed inputs
- return structured outputs
- report errors clearly
- avoid hidden side effects

Implemented tools:
- `filesystem.list`, `filesystem.read_file`, `filesystem.write_file`, `filesystem.move`, `filesystem.delete`, `filesystem.tree`, `filesystem.search`, `filesystem.grep`, `filesystem.semantic_search`
- `shell.run`, `shell.run_safe`
- `process.list`, `process.info`, `process.start`, `process.stop`
- `browser.open_url`, `browser.search_files`, `browser.find_recent`
- `git.status`, `git.log`, `git.diff`, `git.checkout`, `git.clone`, `git.branch`, `git.pull`, `git.push`, `git.commit`, `git.stash`
- `vscode.open_workspace`, `vscode.open_file`, `vscode.list_extensions`, `vscode.install_extension`, `vscode.run_task`, `vscode.diff`, `vscode.read_diagnostics`
- `system.status`, `system.info`, `system.memory`, `system.disk`

Tool outputs should be machine-readable first, human-readable second.

---

## Safety Rules
Never allow silent execution of:
- recursive deletes
- force-overwrites
- arbitrary remote downloads
- credential exfiltration
- privilege escalation
- destructive shell pipelines
- background persistence without explicit consent

High-risk actions must trigger:
1. human-readable explanation
2. exact command or effect preview
3. confirmation path
4. audit log entry

---

## UX Rules
Machina OS should feel:
- calm
- competent
- transparent
- fast
- reversible
- reversible

Avoid:
- overexplaining routine actions
- anthropomorphic fluff
- false confidence
- hidden background activity

Preferred behavior:
- summarize plan briefly
- show progress live
- surface decisions
- offer rollback when possible

---

## MVP Definition
A version is considered MVP when it can reliably do the following on a local machine:

1. Accept a natural language request
2. Produce a structured plan
3. Execute safe filesystem and shell tasks
4. Ask approval for risky steps
5. Log all actions
6. Restore recent task context
7. Open and coordinate a coding workspace in VS Code

Example MVP commands:
- “Open my MES training workspace”
- “Summarize this project folder”
- “Create a Python app skeleton with tests”
- “Prepare the repo and run the dev server”
- “Find the last report I edited and open it”

---

## Definition of Done
A feature is done only if:
- code exists
- tests exist
- logs are emitted
- failure modes are handled
- user-visible behavior is understandable
- dangerous cases are constrained

---

## Coding Guidelines
- Prefer simple modules over clever abstractions
- Type everything important
- Validate all tool inputs
- Keep model prompts versioned
- Store schemas centrally
- Write tests for planners, policies, and tool adapters
- Favor boring technology over fragile wizardry

---

## Prompting Guidelines for Agent Components
When implementing prompts:
- require structured outputs
- forbid pretending to have executed tools
- require the model to mark uncertainty
- require the model to separate observations from decisions
- require the model to ask for approval only when policy requires it

The model should never claim:
- a file was changed unless a tool changed it
- a command ran unless execution output exists
- a repo was updated unless the git tool confirms it

---

## VS Code Integration Goals
Machina OS should integrate with VS Code to:
- open workspaces
- inspect files
- generate code scaffolds
- run tasks
- read diagnostics
- assist debugging
- maintain project-level memory

Eventually, VS Code can act as the primary cockpit for Machina during development.

---

## Build Order

### Machina Seed (Complete ✓)
1. ✅ Local API skeleton — FastAPI on port 8100
2. ✅ Tool registry — typed specs, risk levels, invoke by name
3. ✅ Filesystem tools — list, read, write, move, delete, tree, search
4. ✅ Shell runner with policy checks — command execution + risk gating
5. ✅ Planner/executor loop — intent → plan → step-by-step execution
6. ✅ Structured event log — JSONL + SQLite dual persistence
7. ✅ Chat UI — glassmorphic SPA with SSE streaming
8. ✅ VS Code workspace integration — placeholder registered
9. ✅ Session memory — layered key-value store
10. ✅ Project memory — SQLite-backed with resume support

### Post-Seed Features (Complete ✓)
11. ✅ LLM integration — Ollama + OpenAI/Groq dual provider
12. ✅ LLM-powered intake parsing and plan generation
13. ✅ Approval queue with human-in-the-loop flow
14. ✅ SSE real-time event streaming
15. ✅ Project resume from last known state
16. ✅ SQLite persistence for events and task history
17. ✅ Visual task timeline in UI
18. ✅ Process manager adapter (4 tools)
19. ✅ Browser automation adapter (3 tools)

### Audit-Driven Hardening (Complete ✓)
20. ✅ Plan validator — schema enforcement, step limits, auto-fix
21. ✅ Executor failure recovery — error classification, retry, partial recovery
22. ✅ Capability-based permission model — scoped grants per tool
23. ✅ Telemetry subsystem — plan/tool metrics, success rates, latency tracking
24. ✅ Deterministic planning templates — hybrid planner, dev workflow canonical path
25. ✅ Git adapter — status, log, diff, checkout, clone, branch (6 tools)
26. ✅ Memory class separation — session, task, project, preferences with clear lifecycle

### Tool Protocol Compliance (Complete ✓)
27. ✅ Structured error codes — error_code + message on every ToolResult (FILE_NOT_FOUND, PERMISSION_DENIED, TIMEOUT, etc.)
28. ✅ Output schemas — ToolSpec includes typed output_schema for all tools
29. ✅ Execution limits — hard timeout (120s), output truncation (1 MB), per-invocation enforcement
30. ✅ Filesystem path safety — system directory rejection (Win/POSIX), workspace boundary enforcement for writes/deletes
31. ✅ Shell safety — privilege escalation blocking, destructive command detection
32. ✅ shell.run_safe — read-only shell variant (MEDIUM risk), blocks write/delete/install/network operations
33. ✅ filesystem.tree + filesystem.search — 7 filesystem tools now fully implemented

### Architecture Compliance (Complete ✓)
34. ✅ Schema enhancements — PlanStep.timeout, PlanStep.rollback_hint, Event.severity, Intent.ambiguity_score
35. ✅ ApprovalRequest model — formal data model with approval_id, plan_id, step_id, reason, preview, risk_level, expires_at
36. ✅ Rollback coordinator — executor tracks rollback hints, auto-rollback on failure, coordinated plan rollback
37. ✅ vscode.read_diagnostics — workspace diagnostic tool (pyright, mypy, tsc, eslint)
38. ✅ 9-step dev_workflow — full canonical sequence: tree → git → open → tasks → diagnostics → summarize
39. ✅ analyze_repository intent — deterministic template for comprehensive repo analysis (7 steps)

### Runtime Compliance (Complete ✓)
40. ✅ Task model — Task(task_id, status, goal, workspace_id, intent_id, plan_id, current_step_index, requires_human, last_error, finished_at)
41. ✅ TaskStatus expansion — 13 states: CREATED, INTAKE_COMPLETE, PLANNED, VALIDATED, WAITING_APPROVAL, READY, EXECUTING, PAUSED, COMPLETED, FAILED, ABORTED, ROLLING_BACK, ROLLED_BACK
42. ✅ StepStatus expansion — 10 states: PENDING, BLOCKED, WAITING_APPROVAL, READY, RUNNING, SUCCEEDED, FAILED, SKIPPED, ROLLED_BACK
43. ✅ Event.source — all events tagged with emitting component (core, executor, planner, intake, validator, policy)
44. ✅ Event.severity persistence — source + severity stored in SQLite (with migration for existing DBs)
45. ✅ Task lifecycle in agent core — Task created, status transitions emitted, task_created/task_completed/task_failed/task_paused events
46. ✅ Task management — get_task(), list_tasks(), pause_task(), abort_task() on MachinaCore
47. ✅ Runtime API — POST /tasks, GET /tasks/{id}, POST /tasks/{id}/resume|pause|abort, GET /tasks/{id}/events
48. ✅ Approval API — GET /approvals, POST /approvals/{id}/approve|deny
49. ✅ Tool detail API — GET /tools/{tool_name} returns full ToolSpec
50. ✅ Runtime status API — GET /runtime/status (components, tool count, active tasks, pending approvals)
51. ✅ Max steps limit — reduced from 15 to 12 per runtime spec §11.5
52. ✅ ApprovalRequest enhancements — task_id, status (pending/approved/denied), resolved_at fields

### Event Schema Compliance (Complete ✓)
53. ✅ Canonical event envelope — Event fields renamed: id→event_id, kind→event_type, data→payload, schema_version="1.0"
54. ✅ Envelope-level correlation — task_id, approval_id, workspace_id, correlation_id, trace_id, actor as top-level Event fields
55. ✅ Monotonic sequence numbers — thread-safe counter on EventBus, sequence field on every emitted event
56. ✅ Severity standardization — default severity "INFO", uppercase values (INFO/WARN/ERROR/CRITICAL)
57. ✅ EventBus rewrite — emit() with keyword-only args, SQLite 12-column schema, legacy migration, JSONL persistence
58. ✅ Source taxonomy — all emit sites tagged with source (core, executor, planner, intake, validator, policy)
59. ✅ UI event field migration — JavaScript updated: .kind→.event_type, .data→.payload throughout SPA
60. ✅ Full test suite migration — all 286 tests updated for new event field names

### Runtime Contracts (Complete ✓)
61. ✅ Canonical enums — Severity, PolicyDecision, RiskLevel, TaskStatus, StepStatus, ApprovalStatus, RollbackStatus, RuntimeStatus in core/contracts/enums.py
62. ✅ Prefixed ID generators — make_id() with domain prefixes (task_, plan_, step_, etc.) and optional sequential mode
63. ✅ Runtime snapshot model — RuntimeSnapshot for dashboard status, resume logic, health inspection
64. ✅ Model field additions — Intent.intent_id, Task.last_transition_at/reason, Plan.task_id/planner_version/validation_status, PlanStep.index/risk_level/policy_decision/last_transition_at/reason, ToolResult.message
65. ✅ ApprovalStatus enum — ApprovalRequest.status upgraded from string to canonical ApprovalStatus enum (PENDING/GRANTED/DENIED/EXPIRED/CANCELLED)
66. ✅ Task transition guard — TaskGuard validates all task state changes per MACHINA_STATE_MACHINE §4.4
67. ✅ Step transition guard — StepGuard validates all step state changes per MACHINA_STATE_MACHINE §6.4
68. ✅ Approval transition guard — ApprovalGuard validates one-shot approval lifecycle per §8.3
69. ✅ Enum consolidation — schemas.py imports from core/contracts/enums.py; PolicyDecision moved from policy/engine.py to contracts

### Runtime Infrastructure (Complete ✓)
70. ✅ ValidationState + ToolExecutionStatus enums — added to core/contracts/enums.py (§2.9, §2.10)
71. ✅ EventEmitter — canonical event factory in core/events/emitter.py, bus delegation or standalone+store mode
72. ✅ RuntimeStore — hybrid JSONL + SQLite persistence in core/runtime/store.py (tasks, approvals, snapshots)
73. ✅ TaskRuntime coordinator — core/runtime/coordinator.py wires contracts → guards → emitter → store
74. ✅ Guard-validated task lifecycle — create, transition, persist, emit through TaskRuntime
75. ✅ Approval lifecycle in coordinator — request, grant, deny, cancel, expire with ApprovalGuard enforcement

### Core Integration (Complete ✓)
76. ✅ TaskRuntime wired into MachinaCore — run() uses guard-validated transitions, runtime store for persistence, RuntimeSnapshot for /runtime/status
77. ✅ Step persistence in RuntimeStore — steps table, save_step, get_step, list_steps_for_task with task index ordering
78. ✅ StepRuntime coordinator — step lifecycle (register, transition, start/finish/fail/skip), tool event emission, task synchronisation

### Execution Bridge (Complete ✓)
79. ✅ ToolExecutionError — structured exception class in ToolRegistry for executor error translation
80. ✅ RuntimeExecutor — async execution dispatcher: prime_steps (policy → step status), run_step (tool dispatch via StepRuntime), run_task (iterate with retry for transient errors), StepResult value object
81. ✅ ToolRegistry ToolExecutionError handling — invoke() preserves structured error_code from ToolExecutionError instead of classifying as UNKNOWN_ERROR
82. ✅ Built-in tools layer — core/tools/tools_builtin.py: workspace-bounded filesystem.list, filesystem.read_file, filesystem.write_file, shell.run_safe with ToolExecutionError, binary detection, size limits, shell allowlist
83. ✅ Executor demo — core/tools/executor_demo.py: end-to-end runtime proof script (task → steps → execute → events → snapshot → artifacts)
84. ✅ Executor flow tests — tests/test_executor_flow.py: 12 automated end-to-end tests (read-only flow, approval gate, error handling, event persistence, snapshot, artifact verification)

### Test Infrastructure (Complete ✓)
85. ✅ Shared test configuration — tests/conftest.py: sys.path setup ensuring project root is importable regardless of invocation method
86. ✅ State transition integration tests — tests/test_state_transitions.py: 43 tests verifying task/step/approval lifecycle through runtime coordinators (happy paths, forbidden transitions, terminal states, task sync, persistence, event emission)

### Approval Flow (Complete ✓)
87. ✅ Approval demo — approval_demo.py: end-to-end proof script for human-in-the-loop lifecycle (gate → WAITING_APPROVAL → grant → EXECUTING resume)
88. ✅ Approval flow tests — tests/test_approval_flow.py: 8 automated tests (grant unblocks step/task, denial keeps task blocked, canonical events, snapshot integration)
89. ✅ Bidirectional approval sync — StepRuntime._sync_task_status resumes task from WAITING_APPROVAL → EXECUTING when no steps need approval

### Execution Unification (Complete ✓)
90. ✅ RuntimeExecutor wired into MachinaCore — run() uses guard-validated RuntimeExecutor instead of legacy Executor; StepRuntime registers steps, RuntimeExecutor dispatches through policy → step guards → tool registry
91. ✅ Server.py endpoint migration — all approval/pending/resume/status endpoints use TaskRuntime + StepRuntime instead of legacy Executor; approval API uses canonical approval_id from coordinator
92. ✅ MachinaCore approval management — approve(), deny(), list_pending_approvals(), resume_task() methods using TaskRuntime + StepRuntime; step transitions on approval grant/deny
93. ✅ RuntimeExecutor auto_approve — auto_approve flag bypasses REQUIRE_APPROVAL policy for testing and trusted flows
94. ✅ Stale root-level file cleanup — removed 14 duplicate files (machina_contracts.py, event_emitter.py, runtime_store.py, task_runtime.py, step_runtime.py, executor.py, tool_registry.py, tools_builtin.py, executor_demo.py, etc.)

### Conversational Core — Sprint 5 (Complete ✓)
95. ✅ ConversationSession model — Message, ConversationSession, ConversationStore with SQLite persistence
96. ✅ /chat endpoint — multi-turn conversational API with session management
97. ✅ Context-aware intake — parse_intent_llm_with_context() uses conversation history to resolve references
98. ✅ Context-aware planner — create_plan_llm_with_context() leverages conversation summary
99. ✅ Chat UI rewrite — streaming /chat/stream with token display, session tracking, legacy fallback
100. ✅ Session auto-summary — compresses older messages via LLM when turn count exceeds threshold

### Live Task Controls — Sprint 6 (Complete ✓)
101. ✅ Step retry endpoint — POST /tasks/{id}/retry/{step_id} resets failed step and re-executes
102. ✅ WebSocket live events — /ws endpoint with ConnectionManager, heartbeat, event bus forwarding
103. ✅ Notification integration — toast popups + bell badge + notification panel for approvals/completions/failures
104. ✅ Progress indication — streaming token display with blinking cursor for conversational replies
105. ✅ Task control functions — pauseTask(), abortTask(), retryStep() wired to API endpoints

### Memory & Workspace Intelligence — Sprint 7 (Complete ✓)
106. ✅ Memory browser UI — 4-tab view: scopes, preferences, workspaces, sessions with CRUD operations
107. ✅ Workspace model — Workspace with language/framework detection, key file discovery, git detection
108. ✅ Workspace indexer — index_workspace() walks directory tree, detects languages/frameworks/key files
109. ✅ Workspace persistence — WorkspaceStore with SQLite backend (workspaces.db)
110. ✅ Preferences engine — typed preferences with DEFAULTS dict, get/set/delete/all/reset_all
111. ✅ Memory/workspace/preferences API — CRUD endpoints for all three subsystems

### Background & Notifications — Sprint 8 (Complete ✓)
112. ✅ BackgroundRunner — async task queue with configurable max_concurrent, start/stop/submit
113. ✅ TaskQueue — asyncio.Queue wrapper with priority support
114. ✅ ScheduledTask — recurring task execution with configurable interval
115. ✅ ServiceWatchdog — health check registry, run_checks(), healthy/degraded_services properties
116. ✅ Background API — /background/submit, /background/status, /background/start, /background/stop, /health/detailed

### Polish & Reliability — Sprint 9 (Complete ✓)
117. ✅ Multi-LLM router — LLMRouter with capability-based routing, priority fallback, LLMRoute model
118. ✅ Router wired into MachinaCore — default route + add_llm_route(), conversational replies use router
119. ✅ Error explanation API — POST /explain-error with LLM-powered error analysis and fallback
120. ✅ Keyboard UX — Enter/Escape/ArrowUp/ArrowDown, Ctrl+K/L, Ctrl+1-5 view switching, Alt+N new chat, input history
121. ✅ Smart suggestions — context-aware follow-up suggestions after task completion based on tools used and outcome
122. ✅ Rollback/retry UI — inline retry and explain buttons on failed plan steps, error explanation display
123. ✅ MachinaCore.close() — unified resource cleanup for all SQLite connections
124. ✅ Test cleanup fix — all integration tests use core.close() preventing Windows file lock errors

### Demo Storyboard Hardening — Sprint 10 (Complete ✓)
125. ✅ Heuristic-first intent routing — run(), chat(), chat_stream() prefer heuristic for deterministic intents before LLM fallback
126. ✅ Process visibility — GET /processes API endpoint + list_processes intent with deterministic template
127. ✅ Git integration hardening — branch name in git.status output, dot notation routing, natural language phrasing detection
128. ✅ Failed task UI buttons — Retry/Explain buttons always visible on failed plan steps
129. ✅ Context-aware reference resolution — multi-turn chat resolves ambiguous references from conversation history
130. ✅ Path normalization — 'current directory' and similar phrases normalized to '.' in planner

### Hardening — Sprint 11 (Complete ✓)
131. ✅ Approval expiration enforcement — expire_overdue_approvals() sweeps pending approvals past TTL
132. ✅ Approval TTL default — 5-minute TTL auto-set on request_approval(), configurable via ttl param, ScheduledTask sweeps every 30s
133. ✅ Act 6 end-to-end validation — all sub-tests (memory scopes, preferences, workspace indexing) pass
134. ✅ Full-pipeline integration tests — 4 end-to-end tests: list, read_file, git_status, error_handling with full event/telemetry/persistence verification
135. ✅ Git tool completeness — git.pull, git.push, git.commit, git.stash (4 new tools, 10 total)
136. ✅ Planner git routing — pull, push, commit, stash routed to native tools; commit extracts -m message
137. ✅ Git tool tests — 8 new tests for pull, push, commit (regular + -a), stash (push/pop/list/invalid)

### Workspace Context & System Awareness — Sprint 12 (Complete ✓)
138. ✅ Workspace auto-indexing — run() auto-indexes workspace on first encounter, caches in memory + SQLite
139. ✅ Workspace context in LLM planner — detected languages/frameworks injected into planner system prompt
140. ✅ System monitoring tools — system.info, system.memory, system.disk (stdlib-only, no psutil)
141. ✅ Content search tool — filesystem.grep for text/regex search within files with file pattern filter
142. ✅ Planner routing for new intents — system_info and grep deterministic templates with intake detection
143. ✅ Sprint 12 tests — 24 new tests: system tools, grep, workspace auto-indexing, planner routing, intake

### Compound Workflows & Conversation Intelligence — Sprint 13 (Complete ✓)
144. ✅ Startup diagnostics & resilience — try/except startup with per-subsystem logging, non-blocking tool registration, /health/startup endpoint
145. ✅ Workspace-aware conversational replies — workspace context (languages, frameworks, key files) injected into chat/chat_stream LLM prompts
146. ✅ Compound workflow templates — create_project (Python/JS scaffold), cleanup (tree+git+disk+temp search), find_and_read (search→read chain)
147. ✅ Inter-step output bridging — steps with output_key store output; downstream steps with input_from receive resolved values
148. ✅ Task context in conversation sessions — record_task_outcome() links task results to sessions; get_task_context() injects prior task summaries into LLM prompts
149. ✅ Sprint 13 tests — 34 new tests: compound templates, intake detection, output bridging, task context, workspace-aware prompts, schema fields

### Semantic Filesystem & RAG — Sprint 14 (Complete ✓)
150. ✅ ChromaDB vector store — VectorStore wrapper with graceful degradation, collection-per-workspace, cosine HNSW
151. ✅ Semantic search tool — filesystem.semantic_search with query/workspace_id/n_results parameters
152. ✅ Indexing pipeline — SemanticIndexer with chunking, content-hash dedup, skip filters, explicit-only indexing
153. ✅ RAG-augmented chat — _get_rag_context() injects relevant code snippets into conversational LLM prompts
154. ✅ Index management API — POST /rag/index, GET /rag/status, DELETE /rag/{id}, POST /rag/search, GET /rag/collections
155. ✅ Sprint 14 tests — 47 new tests: vector store, chunking, file indexing, should_index filters, intake, planner, context injection, core integration

### Agent Personality & Response Style — Sprint 15 (Complete ✓)
156. ✅ PersonalityProfile model — Pydantic model with tone, verbosity, emoji, greeting, custom system_instructions
157. ✅ System prompt injection — personality fragment injected into _build_chat_system_prompt for all conversational LLM calls
158. ✅ Preset profiles — 4 built-in presets (default, casual, minimal, detailed) with to_prompt_fragment()
159. ✅ Persistence via preferences — personality stored/loaded via PreferencesEngine, survives restarts
160. ✅ Personality API — GET/PUT /personality, GET /personality/presets, PUT /personality/preset/{name}
161. ✅ UI personality tab — preset selector, tone/verbosity/greeting dropdowns, emoji toggle, custom instructions editor
162. ✅ Sprint 15 tests — 32 new tests: profile model, prompt fragments, presets, core integration, system prompt injection, preferences

### Workflow Composition DSL — Sprint 16 (Complete ✓)
163. ✅ WorkflowDefinition model — Pydantic model (workflow_id, name, description, triggers, variables, steps, enabled) with trigger matching and variable resolution
164. ✅ WorkflowStep model — mirrors PlanStep shape (tool, arguments, output_key, input_from, fallback, timeout, rollback_hint)
165. ✅ WorkflowStore — SQLite-backed CRUD persistence (workflows.db) with save, load, load_by_name, list_all, list_enabled, delete, find_matching
166. ✅ Planner integration — user workflows checked before _plan_general fallback; workflow intent produces workflow-v1 plans with variable resolution
167. ✅ Intake detection — "run workflow X", "execute workflow X", "workflow X" heuristic patterns with workflow_name entity extraction
168. ✅ Compound expansion: refactor — tree → git.status → diagnostics → diff → summary (5-step template)
169. ✅ Compound expansion: debug_issue — diagnostics → git.status → git.log → diff → optional grep → summary (5-6 steps, error-aware)
170. ✅ Workflow API — GET/POST /workflows, GET/PUT/DELETE /workflows/{id} with full CRUD
171. ✅ Workflow Composer UI — visual step editor, trigger/variable configuration, enable/disable toggle, edit/delete controls
172. ✅ Sprint 16 tests — 40 new tests: model creation, trigger matching, variable resolution, store CRUD, planner integration, intake detection, compound expansion

### Multi-Agent Coordination — Sprint 17 (Complete ✓)
173. ✅ AgentDefinition model — Pydantic model with agent_id, name, capabilities, tool_filter (fnmatch globs), system_prompt, enabled
174. ✅ BUILTIN_AGENTS — filesystem, git, shell, system agents with scoped tool_filter and capabilities
175. ✅ AgentPool — register/unregister/find agents by capability, intent, or tool with enabled_only filtering
176. ✅ AgentBus — inter-agent pub/sub messaging with send, broadcast, subscribe (by agent/type/all), capped history
177. ✅ PlanStep.delegate_to — optional agent_id field for scoped delegation in plan steps
178. ✅ RuntimeExecutor delegation — AGENT_TOOL_DENIED gating + delegation events on agent bus
179. ✅ Intake delegate detection — "delegate to"/"ask agent"/"use agent"/"send to agent" patterns with agent_name extraction
180. ✅ Planner delegate template — deterministic _plan_delegate() for delegation intent
181. ✅ Agent API + UI — 7 CRUD endpoints, Agents view (7th tab) with editor, message log, Ctrl+1-7
182. ✅ Sprint 17 tests — 53 new tests: agent model, pool, bus, delegation schema, intake, planner, executor delegation, core integration

### Agent Orchestration & Decomposition — Sprint 18 (Complete ✓)
183. ✅ OrchestrationStrategy enum — SINGLE, ROUND_ROBIN, CAPABILITY_SCORE, FALLBACK, PIPELINE with OrchestrationConfig model
184. ✅ Agent scoring — score_agent_for_tool() with specificity scoring (exact=1.0, prefix glob=0.3+, open=0.1)
185. ✅ AgentPool strategy-aware selection — candidates_for_tool() sorted by score, select_agent() with configurable strategy
186. ✅ Executor fallback delegation — FALLBACK strategy tries candidates_for_tool() before AGENT_TOOL_DENIED
187. ✅ Executor pipeline execution — run_pipeline() chains agents sequentially with output passing
188. ✅ Agent-aware LLM planner — agent catalog injected into system prompt, delegate_to parsed from LLM output
189. ✅ Planner agent pool wiring — _plan_delegate() resolves agents from pool, routes to agent-specific tools
190. ✅ Task decomposition — decompose_for_agents() decomposes complex intents into agent-scoped sub-plans
191. ✅ MachinaCore orchestration wiring — orchestration property, set_orchestration(), agent-aware chat prompts
192. ✅ Orchestration API + UI — GET/PUT /orchestration endpoints, strategy panel in Agents view
193. ✅ Sprint 18 tests — 43 new tests: strategy enum, config, scoring, pool selection, planner delegation, decomposition, pipeline, core integration

### Agent Persistence & Delegation Chains — Sprint 19 (Complete ✓)
194. ✅ AgentStore SQLite — WAL-mode SQLite CRUD for user-created agents (agents.db), save/load/load_all/delete/exists
195. ✅ AgentPool store integration — register/unregister auto-persist non-builtins, load persisted agents on init, _builtin_ids isolation
196. ✅ MachinaCore wiring — creates AgentStore, passes to AgentPool, closes in close()
197. ✅ DelegationChain class — push/pop path tracking, would_cycle() detection, would_exceed_depth() guard, max_depth=5
198. ✅ AgentBus delegation management — create_chain/get_chain/remove_chain, delegate() with cycle/depth validation
199. ✅ RuntimeExecutor chain validation — creates DelegationChain per step, DELEGATION_CYCLE error code on cycle detection, fallback chain safety checks
200. ✅ Sprint 19 tests — 38 new tests: store CRUD, pool persistence, delegation chains, bus delegation, executor chain validation, core integration

### Consensus, Delegation Viz & Agent Memory — Sprint 20 (Complete ✓)
201. ✅ ConsensusStrategy/VoteValue/ConsensusStatus enums — MAJORITY/UNANIMOUS/WEIGHTED strategies, APPROVE/REJECT/ABSTAIN votes
202. ✅ ConsensusRequest model — question, candidates, votes dict, strategy, min_voters, resolve() with majority/unanimous/weighted logic
203. ✅ AgentBus consensus methods — request_consensus, cast_vote, resolve_consensus, get_consensus, list_consensus_requests
204. ✅ Consensus events — consensus_requested, consensus_vote, consensus_resolved emitted on agent bus
205. ✅ OrchestrationConfig consensus fields — consensus_strategy + consensus_min_voters
206. ✅ Delegation chain API + UI — GET /agents/delegation-chains, visual chain path display with depth indicators
207. ✅ Agent memory scope — MemoryStore 'agent' scope with set/get/delete/list/clear per-agent methods
208. ✅ Agent memory API — GET/PUT/DELETE /agents/{id}/memory with isolation between agents
209. ✅ Consensus API — POST/GET /consensus, POST /consensus/{id}/vote, POST /consensus/{id}/resolve
210. ✅ UI: Consensus panel — create form, vote/resolve buttons, status display in Agents view
211. ✅ UI: Agent Memory section — agent selector, key-value viewer, delete controls
212. ✅ Sprint 20 tests — 54 new tests: consensus models, voting logic, bus integration, agent memory, delegation listing, core integration

### Negotiation, Consensus Executor & Capability Learning — Sprint 21 (Complete ✓)
213. ✅ NegotiationPhase/NegotiationPriority enums — 7 phases (PROPOSED→WITHDRAWN), 4 priority levels (CRITICAL=1→LOW=4)
214. ✅ NegotiationProposal model — full lifecycle: propose, counter (multi-round), accept, reject, withdraw, resolve_by_priority; is_terminal property, max_rounds enforcement
215. ✅ AgentBus negotiation methods — start_negotiation, counter_negotiation, accept_negotiation, reject_negotiation, resolve_negotiation_by_priority, get_negotiation, list_negotiations (with agent/tool/task/active filters)
216. ✅ Negotiation events — negotiation_proposed, negotiation_countered, negotiation_accepted, negotiation_rejected, negotiation_resolved emitted on agent bus
217. ✅ Negotiation API — POST/GET /negotiations, GET /negotiations/{id}, POST /negotiations/{id}/counter, /accept, /reject, /resolve
218. ✅ Negotiation UI — create form with priority selector, negotiation cards with phase-colored badges, counter/accept/reject/auto-resolve buttons
219. ✅ CapabilityScore model — agent_id, tool, successes, failures, total_duration_ms, error_counts, confidence formula (success_rate × min(1, samples/20))
220. ✅ RuntimeExecutor capability recording — _record_capability() persists scores to agent memory after each delegated tool execution
221. ✅ RuntimeExecutor consensus-aware execution — run_step_with_consensus() gates tools on multi-agent consensus; auto-voting by confidence; CONSENSUS_REJECTED error code
222. ✅ Capability API + UI — GET /agents/{agent_id}/capabilities endpoint, Capability Learning panel with agent selector and table display
223. ✅ Sprint 21 tests — 58 new tests: negotiation models/lifecycle, bus negotiation, capability scoring, consensus-aware executor, capability recording, core integration

### Negotiation Strategies, Reputation, Consensus Learning & Handoffs — Sprint 22 (Complete ✓)
224. ✅ AgentReputation model — cross-task aggregation with total_successes/failures, tools_used dict, recent_outcomes list, reputation_score (40% lifetime + 60% recent × sample_confidence)
225. ✅ ConsensusPatternScore model — per-tool pattern tracking with approval_rate, should_skip_consensus (≥10 samples and >95% approval)
226. ✅ HandoffStatus/HandoffRequest models — full lifecycle (REQUESTED→ACCEPTED→EXECUTING→COMPLETED/FAILED/DECLINED/CANCELLED) with preconditions, constraints, reason, is_terminal
227. ✅ suggest_counter_agents() — heuristic ranking of alternative agents by capability confidence, excludes proposed agent
228. ✅ AgentBus auto_counter — picks best alternative via suggest_counter_agents(), submits counter-proposal, broadcasts negotiation_auto_countered
229. ✅ AgentBus consensus pattern learning — record_consensus_outcome, get_consensus_pattern, list_consensus_patterns, should_skip_consensus
230. ✅ AgentBus handoff protocol — request_handoff, accept_handoff, decline_handoff, complete_handoff, fail_handoff, cancel_handoff, get_handoff, list_handoffs (with agent_id/task_id/active_only filters)
231. ✅ RuntimeExecutor dynamic consensus skip — should_skip_consensus check before candidate lookup, consensus outcome recording after resolution
232. ✅ RuntimeExecutor reputation recording — _record_capability() also records AgentReputation to agent memory, get_agent_reputation() returns cross-task metrics
233. ✅ Reputation API — GET /agents/{agent_id}/reputation
234. ✅ Negotiation auto-counter API — POST /negotiations/{negotiation_id}/auto-counter
235. ✅ Consensus patterns API — GET /consensus/patterns, GET /consensus/patterns/{tool}
236. ✅ Handoff API — POST/GET /handoffs, GET /handoffs/{id}, POST /handoffs/{id}/accept, /decline, /complete, /cancel
237. ✅ UI: Agent Reputation panel — agent selector, reputation/success score cards, tools used badges
238. ✅ UI: Consensus Patterns table — tool pattern, approvals/rejections, approval rate, auto-skip indicator
239. ✅ UI: Task Handoffs panel — create form, status-colored cards, accept/decline/complete/cancel buttons
240. ✅ UI: Auto-Counter button — on active negotiation cards next to Auto-Resolve
241. ✅ Sprint 22 tests — 69 new tests: reputation model, consensus patterns, handoff lifecycle, suggest_counter_agents, bus auto-counter/patterns/handoffs, executor reputation, core integration

### Agent Health, Discovery, Workflow Chains & Performance — Sprint 23 (Complete ✓)
242. ✅ AgentHealthStatus enum — ONLINE, DEGRADED, OFFLINE with automatic state transitions
243. ✅ AgentHealthRecord model — rolling health snapshot with consecutive failure/success tracking, latency monitoring, degradation detection, recovery thresholds
244. ✅ AgentWorkflowStep/AgentWorkflowChain models — multi-step delegation sequences with agent_id→tool mapping, output_key/input_from bridging, agent_sequence property
245. ✅ DiscoveredCapability model — inferred capabilities from filter (tool_filter globs) or history (execution data) sources with confidence scores
246. ✅ AgentBus health monitoring — record_health_check (auto-evaluate status), get_agent_health, list_agent_health, set_agent_status (manual override), agent_health_changed events
247. ✅ AgentBus workflow chains — create_workflow_chain, get_workflow_chain, list_workflow_chains, delete_workflow_chain with workflow_chain_created/deleted events
248. ✅ RuntimeExecutor health recording — _record_capability() records health checks via bus after each delegated tool execution
249. ✅ RuntimeExecutor capability discovery — discover_capabilities() expands tool_filter globs against registry + merges execution history from memory
250. ✅ RuntimeExecutor performance snapshots — get_agent_performance() returns combined health, reputation, capabilities, and discovered capabilities
251. ✅ Health API — GET /agents/health, GET /agents/{id}/health, POST /agents/{id}/health/status
252. ✅ Capability discovery API — GET /agents/{id}/capabilities/discovered
253. ✅ Performance API — GET /agents/{id}/performance, GET /agents/performance/comparison
254. ✅ Workflow chains API — POST/GET /workflow-chains, GET/DELETE /workflow-chains/{id}
255. ✅ UI: Agent Health panel — status indicators (green/amber/red), error streak, latency, degraded_since display
256. ✅ UI: Capability Discovery panel — agent selector, tool/source/confidence table with filter/history badges
257. ✅ UI: Performance Dashboard — compare all agents with reputation score, success rate, latency metric cards
258. ✅ UI: Workflow Chains panel — create form with dynamic step editor, chain visualization with agent→tool flow arrows, delete controls
259. ✅ Sprint 23 tests — 49 new tests: health status/record, workflow chains, discovery, bus health/chains/events, executor recording/discovery/performance, core integration

### Health Persistence, Chain Execution, Trends & Auto-Routing — Sprint 24 (Complete ✓)
260. ✅ HealthStore SQLite — WAL-mode SQLite persistence (health.db) with three tables: health_checks, health_snapshots, performance_trends
261. ✅ AgentBus health auto-persist — record_health_check() writes checks + snapshots to SQLite, _load_health_snapshots() restores on startup
262. ✅ AgentBus trend methods — record_performance_trend(), get_health_checks(), get_health_trends() with health_store delegation
263. ✅ Workflow chain execution — RuntimeExecutor.run_workflow_chain() converts chain steps → PlanSteps, sequential execution with output bridging, stops on failure
264. ✅ Performance trend recording — _record_capability() records time-series trend data (reputation_score, success_rate, avg_latency_ms, health_status) after each delegated execution
265. ✅ get_agent_performance() trends — performance endpoint now includes trends data from health_store
266. ✅ Health-aware auto-routing — AgentPool.candidates_for_tool() excludes OFFLINE agents, deprioritizes DEGRADED (sort by health_tier then specificity)
267. ✅ AgentPool.agent_bus wiring — optional AgentBus parameter for health-aware routing, wired in MachinaCore
268. ✅ HealthStore in MachinaCore — health.db created, passed to AgentBus, closed on core.close()
269. ✅ Workflow chain execution API — POST /workflow-chains/{chain_id}/execute
270. ✅ Health history API — GET /agents/{agent_id}/health/history
271. ✅ Health trends API — GET /agents/{agent_id}/health/trends
272. ✅ UI: Health History panel — agent dropdown, check log with success/failure dots, latency, errors, timestamps
273. ✅ UI: Performance Trends panel — agent dropdown, 3-card summary (Score, Success%, Latency), sparkline bar chart
274. ✅ UI: Workflow chain Execute button — inline execute button on chain cards
275. ✅ Sprint 24 tests — 38 new tests: HealthStore CRUD (checks/snapshots/trends), bus persistence/loading/trends/history, workflow chain execution (success/multi-step/failure/task_id), pool health-aware routing (offline/degraded/healthy/no-bus/select/all-offline), executor trend recording, core integration (wiring/persistence/restart)

### Intelligent Recovery & Pipeline Evolution — Sprint 25 (Complete ✓)
276. ✅ Enhanced output bridging — _bridge_step_input() injects _prior_output key, resolves path from files/matches/string/list, forwards non-underscore dict keys via setdefault
277. ✅ Condition evaluation — RuntimeExecutor.evaluate_condition() parses `output_key:field op value`, supports ==, !=, contains, not_empty operators
278. ✅ Conditional pipeline branching — AgentWorkflowStep.condition field, run_workflow_chain() evaluates conditions before each step, skips unmet conditions via skip_step()
279. ✅ Agent auto-healing in run_step — detects DEGRADED/OFFLINE agents before delegation, finds healthy candidates, reroutes step, emits agent_auto_healed event
280. ✅ AgentBus.auto_heal() — finds healthy replacement agent from candidates, skips self and unhealthy, emits agent_auto_healed event
281. ✅ SVG time-series trend chart — replaced sparkline bar chart with dual-line SVG chart (amber=reputation_score, green=success_rate) in Performance Trends panel
282. ✅ UI condition field — workflow step editor has condition input, submission includes condition, chain cards show ⚡condition badge
283. ✅ Auto-heal API — POST /agents/{agent_id}/auto-heal endpoint for manual heal trigger
284. ✅ Sprint 25 tests — 41 new tests: output bridging (8), condition evaluation (13), conditional chain execution (3), auto-heal run_step (3), bus auto_heal (5), chain output bridging (2), workflow step condition (3), core integration (3)

### Autonomous Agent Lifecycle — Sprint 26 (Complete ✓)
285. ✅ Auto-healing scheduler — ScheduledTask (60s interval) in MachinaCore._health_sweeper, _sweep_agent_health() iterates agent health records, probes tool_filter patterns, calls auto_heal() for DEGRADED/OFFLINE agents
286. ✅ Workflow chain templates — BUILTIN_CHAIN_TEMPLATES dict with 3 pre-built chains: code-review (tree→git→grep→read), deploy-check (git→log→memory→disk), project-scan (tree→search→git→info)
287. ✅ AgentBus.create_chain_from_template() — instantiates AgentWorkflowChain from built-in template by name, returns chain or None
288. ✅ Agent lifecycle events — AgentPool.register() emits agent_registered, unregister() emits agent_unregistered on agent bus
289. ✅ Agent summary API — GET /agents/summary returns total, online, degraded, offline counts + top_agent + top_score
290. ✅ Template APIs — GET /workflow-chain-templates lists available templates, POST /workflow-chains/from-template/{template_id} creates chain from template
291. ✅ UI: Agent status bar — fleet health summary strip with online/degraded/offline dot counts + top performer display
292. ✅ UI: Chain template picker — "Use Template" button, template card list with name/description/step count, one-click chain creation
293. ✅ Sprint 26 tests — 28 new tests: chain templates (6), bus template creation (4), lifecycle events (5), auto-healing scheduler (6), agent summary (2), core integration (5)

### Cross-Agent Pipelines & Communication — Sprint 27 (Complete ✓)
294. ✅ Cross-agent conditional branching — AgentWorkflowStep.branch_to field, executor re-routes steps to alternate agent when condition fails instead of skipping
295. ✅ Pipeline capability negotiation — PipelineNegotiationResult model, AgentBus.negotiate_pipeline() scores candidates by confidence, detects ties as conflicts
296. ✅ Agent request/response protocol — AgentRequest/AgentResponse models with lifecycle (PENDING→DELIVERED→RESPONDED), AgentBus send_request/send_response/list_requests
297. ✅ Workflow chain versioning — version/version_history/updated_at on AgentWorkflowChain, snapshot(), update_steps(), rollback() methods
298. ✅ Bus chain versioning — AgentBus.update_workflow_chain() and rollback_workflow_chain() with events
299. ✅ API endpoints — 7 new endpoints: POST/GET /agent-requests, /agent-requests/{id}, /agent-requests/{id}/respond, /workflow-chains/{id}/negotiate, PUT /workflow-chains/{id}, /workflow-chains/{id}/rollback, /workflow-chains/{id}/versions
300. ✅ UI panels — Agent Requests panel (form, status list, respond), chain version/negotiate/rollback/history buttons, branch_to badges and step editor field
301. ✅ Sprint 27 tests — 44 new tests: request model (7), pipeline negotiation result (1), branching (3), chain versioning (8), bus request/response (7), bus negotiation (4), bus chain versioning (6), executor branching (2), core integration (6)

### Agent Communication & Execution History — Sprint 28 (Complete ✓)
302. ✅ BroadcastQuery model — query_id, from_agent, question, target_agents, responses dict, status lifecycle (PENDING→COLLECTING→COMPLETED), add_response(), complete()
303. ✅ AgentBus broadcast methods — broadcast_query, respond_to_query, complete_query, get_query, list_queries with active_only filter and events
304. ✅ CapabilityAnnouncement model — announcement_id, agent_id, capabilities list, tool_filter list with bus announce/list methods and events
305. ✅ ChainExecutionRecord model — execution_id, chain_id, chain_name, status (RUNNING/SUCCESS/PARTIAL/FAILED), step counters, finish() method
306. ✅ AgentBus chain execution methods — record_chain_execution, list_chain_executions, get_chain_execution with events
307. ✅ RuntimeExecutor chain recording — run_workflow_chain() auto-records execution history via agent bus after completion
308. ✅ CollaborationSession model — session_id, task_id, participants, shared context dict, join/leave/set_context/close lifecycle
309. ✅ AgentBus collaboration methods — create/join/leave/set_context/close/list collaborations with events
310. ✅ API endpoints — 17 new endpoints for broadcast queries, capability announcements, chain executions, collaborations
311. ✅ UI panels — 4 new panels: Broadcast Queries, Chain Execution History, Capability Announcements, Collaboration Sessions
312. ✅ Sprint 28 tests — 49 new tests: broadcast query model (5), announcement model (1), execution record model (4), collaboration model (5), bus broadcasts (8), bus announcements (3), bus chain history (4), bus collaborations (10), executor chain recording (2), core integration (6)

### Pipeline Replay, Broadcast Aggregation & Agent Task Queue — Sprint 29 (Complete ✓)
313. ✅ ChainReplayRequest model — replay_id, source_execution_id, chain_id, chain_name, override_arguments, result_execution_id
314. ✅ BroadcastAggregation model — aggregation_id, query_id, strategy (ALL/FIRST/MERGE/MAJORITY), result, response_count
315. ✅ AgentTaskItem model — item_id, agent_id, tool, arguments, priority (1-5), status lifecycle (QUEUED→RUNNING→COMPLETED/FAILED/CANCELLED)
316. ✅ AgentBus replay methods — request_chain_replay, get_chain_replay, list_chain_replays, complete_chain_replay with events
317. ✅ AgentBus aggregation methods — aggregate_broadcast (4 strategies), expire_broadcast_query with events
318. ✅ AgentBus task queue methods — enqueue_task (priority-sorted), dequeue_task, complete/fail/cancel_task_item, list/get with events
319. ✅ RuntimeExecutor replay — replay_workflow_chain() re-creates chain from execution record, applies overrides, links replay to result
320. ✅ API endpoints — 15 new endpoints for chain replays, broadcast aggregation/expiry, agent task queue CRUD
321. ✅ UI panels — Agent Task Queue panel (enqueue form, priority-sorted list, dequeue/complete/cancel), Replay button on executions, Aggregate/Expire buttons on broadcasts
322. ✅ Sprint 29 tests — 46 new tests: replay model (3), aggregation model (2), task item model (6), bus replay (5), bus aggregation (10), bus task queue (13), executor replay (2), core integration (6)

### Task Queue Auto-Execution, Broadcast Timeouts & Pipeline Wizard — Sprint 30 (Complete ✓)
323. ✅ BroadcastQuery.timeout_ms — configurable timeout field (0 = no timeout), is_overdue property
324. ✅ AgentBus.broadcast_query() timeout_ms — keyword argument support, passed to model constructor
325. ✅ AgentBus.expire_overdue_queries() — sweeps all queries, expires overdue, returns expired list
326. ✅ RuntimeExecutor.auto_execute_task() — dequeues task item, invokes tool via registry, completes/fails item
327. ✅ RuntimeExecutor.auto_execute_agent_queue() — drains all QUEUED tasks for agent in priority order
328. ✅ MachinaCore._broadcast_sweeper — ScheduledTask (30s interval), _sweep_broadcast_timeouts() method
329. ✅ API endpoints — 3 new: POST /agent-tasks/{id}/auto-execute, POST /agent-tasks/auto-execute-queue/{agent_id}, POST /broadcast-queries/with-timeout
330. ✅ UI: Auto-Execute buttons — ⚡ Auto-Execute on QUEUED items, Auto-Execute All for batch processing
331. ✅ UI: Broadcast timeout — timeout_ms input field on form, timeout badge on query cards
332. ✅ UI: Pipeline wizard — agent/tool dropdown selectors from API, step reordering (▲/▼), step numbering
333. ✅ Sprint 30 tests — 29 new tests: broadcast timeout model (5), bus timeout (8), auto-execute task (5), auto-execute queue (4), core integration (7)

### Capability Auto-Discovery, Parallel Chain Execution & Smart Task Scheduling — Sprint 31 (Complete ✓)
334. ✅ AgentWorkflowStep.parallel_group — optional group key for concurrent execution within chains
335. ✅ AgentPool.best_agent_for_tool() — capability-confidence selection with memory store lookup, specificity fallback
336. ✅ RuntimeExecutor.schedule_task() — auto-routes task to best agent, enqueues on bus, returns {status, agent_id, item_id, confidence}
337. ✅ RuntimeExecutor.run_workflow_chain_parallel() — groups steps by parallel_group, runs groups sequentially but concurrent within group via asyncio.gather, falls back to sequential when no groups
338. ✅ MachinaCore._discovery_sweeper — ScheduledTask (90s interval), _sweep_capability_discovery() discovers capabilities for all agents
339. ✅ Bug fix: core.executor → core.runtime_executor in server.py auto-execute endpoints (2 locations)
340. ✅ API endpoints — 5 new: POST /tasks/schedule, POST /workflow-chains/{id}/execute-parallel, POST /discovery/run, GET /discovery/status
341. ✅ UI: Smart Task Scheduling panel — tool/args/priority form, schedule to best agent, result display
342. ✅ UI: Discovery Status panel — run discovery sweep, agent capability list with source/confidence badges
343. ✅ UI: Parallel chain support — parallel_group input in step editor, ∥ Parallel execute button, parallel_group badges on chain cards
344. ✅ Sprint 31 tests — 28 new tests: parallel_group model (4), best_agent_for_tool (5), schedule_task (5), parallel chain execution (7), core integration (7)

### Intent Hardening & LLM Guardrails — Sprint 32 (Complete ✓)
345. ✅ Dynamic tool-name routing — registry-based detection of dot-notation tool names (system.info, filesystem.list, etc.) via startup-populated _tool_registry_names set, prefix-to-intent mapping, filesystem sub-intent refinement
346. ✅ LLM intent guardrail — _query_has_tool_signal() last-resort check: when both LLM and heuristic classify as general, detects registered tool names in raw query to force task routing
347. ✅ Human-readable output formatting — _format_system_output() for system.info/memory/disk/status, _format_dict_output() for generic dicts; replaces raw JSON dumps in plan result summaries
348. ✅ Stale session cleanup — ConversationStore.purge_stale(max_age_days, min_messages) deletes old/empty sessions; DELETE /conversations/purge API endpoint
349. ✅ Server port conflict auto-recovery — _check_port() at startup detects busy port, identifies holder via netstat/lsof, auto-kills stale process (Windows + POSIX)
350. ✅ Sprint 32 tests — 37 new tests: dynamic routing (15), tool-signal guardrail (5), output formatting (10), session purge (4), port check (2), core integration (1)

### Pipeline Wizard & Cross-Agent Optimization — Sprint 33 (Complete ✓)
351. ✅ AgentBus.optimize_chain() — dependency graph analysis via output_key/input_from, topological grouping into parallel execution groups
352. ✅ AgentBus.apply_optimization() — applies parallel groups as annotations on chain steps in-place
353. ✅ AgentBus.auto_assign_chain() — uses negotiate_pipeline to assign best agents to chain steps by capability confidence
354. ✅ Pipeline wizard drag-and-drop — HTML5 drag reordering with drag handles, visual feedback during drag
355. ✅ Enhanced step editor — description, output_key, input_from, arguments (JSON), condition, branch_to, parallel_group fields per step with prefill support
356. ✅ Auto-Assign Agents button — creates temp chain, negotiates via pipeline, assigns best agents to form dropdowns
357. ✅ Vertical flow visualization — _renderChainStepFlow() with colored badges: output_key (emerald), input_from (sky), condition (amber), branch_to (cyan), parallel_group (teal), args (slate)
358. ✅ Optimize button on chain cards — POSTs to /optimize, applies parallel groups, shows toast with group count
359. ✅ Auto-Assign button on chain cards — POSTs to /auto-assign, refreshes chain list with updated agent assignments
360. ✅ API endpoints — POST /workflow-chains/{id}/auto-assign, /optimize, /apply-optimization
361. ✅ Sprint 33 tests — 26 new tests: optimize_chain (7), apply_optimization (3), auto_assign_chain (4), step editor fields (4), complex optimization (3), core integration (5)

### Workspace Shell Interface — Sprint 34 (Complete ✓)
362. ✅ File browse API — POST /files/browse endpoint with directory listing via filesystem.list tool
363. ✅ File read API — POST /files/read endpoint with content preview (100KB cap) via filesystem.read_file tool
364. ✅ Process detail API — GET /processes/{pid} endpoint via process.info tool
365. ✅ Process stop API — POST /processes/{pid}/stop endpoint via process.stop tool
366. ✅ System status dashboard API — GET /system/status combined endpoint: tools count, system info/memory/disk, agent fleet stats, active tasks
367. ✅ File Explorer view — split-panel layout with directory tree (breadcrumb, go-up, refresh) and file preview (syntax-aware icons, formatted sizes)
368. ✅ Process Monitor view — sortable table (PID, Name, Status, CPU%, Memory) with search filter, stop button with confirmation, process stats
369. ✅ Command Palette — Ctrl+K fuzzy search overlay with keyboard navigation (ArrowUp/Down, Enter, Escape), categories (Views, Actions, Tools), unmatched queries sent to Neural Link
370. ✅ System Status Bar — persistent bottom bar with workspace hostname, active task count, agent fleet status (online/total), memory usage, 30s polling
371. ✅ View system expansion — 9 views (added Explorer + Processes), Ctrl+1-9 keyboard shortcuts, nav tabs, dock buttons
372. ✅ Sprint 34 tests — 31 new tests: file browse API (4), file read API (2), process endpoints (3), system status (3), command palette (4), view system (3), file helpers (7), core integration (5)

### Metrics & Observability Dashboard — Sprint 35 (Complete ✓)
373. ✅ EventBus query enhancements — query_events() source/severity filters, ORDER BY rowid DESC (newest first), event_types(), event_sources(), event_count() methods
374. ✅ Metrics dashboard API — GET /metrics/dashboard (combined plan_summary + tool_summary + tool_errors + event_count)
375. ✅ Events query API — GET /events/query with type/source/severity/plan_id filters, pagination (limit/offset), total count
376. ✅ Events meta API — GET /events/meta returns distinct types, sources, severities for filter dropdowns
377. ✅ Settings API — GET /settings/info (system info), GET/PUT/DELETE /settings/preferences (preference CRUD)
378. ✅ Metrics view — stitch performance_monitor style: 4 overview cards (success rate, avg steps, duration, event count), SVG bar chart with success overlay, tool performance table, error list
379. ✅ Event Inspector view — filter bar (type/source/severity dropdowns), paginated event table with severity badges, newest-first ordering
380. ✅ Settings view — glass-panel system info (neon-glow-primary, backdrop-blur), preferences CRUD, performance bars (neon progress with box-shadow), RAG index status
381. ✅ View system expansion — 12 views (added Metrics, Events, Settings), nav tabs, dock buttons, Ctrl+0 for Metrics, command palette entries
382. ✅ Sprint 35 tests — 29 new tests: event filtering (13), API shapes (5), UI structure (11)

### Next Priorities
- Agent capability negotiation improvements
- Pipeline construction wizard with drag-and-drop agent assignment (visual drag between agents)
- Agent-to-agent communication dashboard

---

## First Milestone — Machina Seed ✓ ACHIEVED

The system can:
- ✅ Interpret a simple request (LLM-assisted or heuristic fallback)
- ✅ Create a structured plan with typed steps
- ✅ Execute 3–5 tool steps safely with policy checks
- ✅ Show the full execution trace (events view + timeline)
- ✅ Recover from failed steps (executor handles errors per-step)
- ✅ Reopen the same project context (project resume via `/resume`)

**1579 tests passing. 382 build items complete.**

---

## Architecture Bias
When design tradeoffs appear, prefer:
- inspectability over opacity
- local execution over remote dependence
- tool truth over model narration
- constraints over hype
- reliable narrow competence over broad fake competence

---

## Notes for Contributors
This project is trying to make operating environments more intent-native, not just add a chatbot to a desktop.

Whenever you build a feature, ask:
- Does this increase real capability?
- Is the behavior inspectable?
- Can the user trust what happened?
- Would this still be useful if the model were imperfect?

If the answer is no, redesign it.

---

## Canonical One-Sentence Summary
**Machina OS is a local-first, intent-driven operating layer that turns natural-language goals into safe, inspectable system actions.**
