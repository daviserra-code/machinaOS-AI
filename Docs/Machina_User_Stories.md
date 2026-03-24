# Machina_User_Stories.md

## Positioning

**Machina OS is a local-first AI operating layer for developer and technical workflows.**

Practical positioning variants:
- AI-native workspace shell
- Inspectable agent runtime for engineering work
- Governed execution layer for developer workflows
- Local-first orchestration shell for code, tools, and agents

Machina should usually be described as an operating layer or workspace shell, not as a new kernel or desktop replacement OS.

---

## Core value proposition

Machina helps technical users turn intent into visible, governed execution inside a workspace.

It is most useful for:
- understanding codebases
- preparing environments
- debugging issues
- running repeatable technical workflows
- coordinating specialized agents
- doing all of that with approvals, traceability, and runtime truth

---

## Flagship user stories

### 1. Repo onboarding
**As a developer**, I want to understand an unfamiliar codebase quickly so I can become productive fast.

**Prompt example**  
> Scan this workspace, tell me what stack it uses, what the key files are, and where I should start.

**What Machina does**
- scans the workspace
- detects stack clues
- identifies key files and entry points
- reads README/config files
- summarizes architecture hints
- shows which tools and steps were used

**Outcome**  
The developer understands the project in minutes instead of manually exploring for an hour.

---

### 2. Environment preparation
**As a developer**, I want Machina to prepare my project workspace so I can start working without manual setup friction.

**Prompt example**  
> Prepare this project for work.

**What Machina does**
- inspects the repo
- checks project structure
- opens the workspace context
- runs safe setup commands where allowed
- surfaces missing dependencies or issues
- asks for approval before riskier actions

**Outcome**  
Project setup becomes a guided execution flow instead of a manual checklist.

---

### 3. Debug workflow
**As an engineer**, I want Machina to help me inspect an issue across code, diagnostics, and repo state.

**Prompt example**  
> Debug this issue in the current workspace.

**What Machina does**
- reads diagnostics
- searches code semantically
- checks repo state and diffs
- runs safe commands
- chains the investigation as a workflow
- summarizes likely causes and next actions
- keeps the event trace visible

**Outcome**  
Debugging becomes structured, inspectable, and faster.

---

## Extended user stories

### 4. Technical review
**As a tech lead or reviewer**, I want a quick summary of project state and risky areas before reviewing changes.

**Prompt example**  
> Inspect this repo, summarize the current state, and show me risky areas.

**What Machina does**
- checks repo contents and status
- inspects diagnostics
- highlights high-risk files or changes
- exposes runtime steps and events
- requires approval for any mutating actions

**Outcome**  
Technical review starts with a reliable operational snapshot.

---

### 5. Consultancy discovery
**As a consultant or solutions engineer**, I want to map a client project quickly and identify the important integration points.

**Prompt example**  
> Map the project, explain the architecture clues, and highlight integration points.

**What Machina does**
- scans the workspace structure
- identifies frameworks and languages
- reads key project files
- uses semantic search for concepts
- stores findings as reusable context

**Outcome**  
Discovery work becomes faster and more repeatable.

---

### 6. Repeatable engineering workflows
**As an engineering team**, we want to convert repeated routines into reusable workflows.

**Prompt example**  
> Run the refactor workflow.

**What Machina does**
- loads a predefined workflow
- executes ordered steps
- passes context between steps
- records execution history
- lets users inspect, retry, or approve steps

**Outcome**  
Operational routines become reusable AI-native workflows instead of tribal knowledge.

---

### 7. Multi-agent coordination
**As a user**, I want specialized agents to collaborate on a task without manually orchestrating them.

**Prompt example**  
> Have one agent inspect the repo, another analyze diagnostics, and a third summarize the likely fix path.

**What Machina does**
- assigns specialized roles
- delegates work
- shows handoffs and message flow
- preserves approvals and event trace
- presents a combined result

**Outcome**  
Complex analysis becomes coordinated and inspectable instead of fragmented.

---

### 8. Safe governed automation
**As a stakeholder or reviewer**, I want to see AI execution without giving the system uncontrolled power.

**Prompt example**  
> Run a gated command in this sandbox.

**What Machina does**
- shows the plan before action
- pauses for approval on gated steps
- exposes timeline, metrics, and events
- allows approve / deny / retry / explain
- runs inside a sandboxed workspace

**Outcome**  
The system demonstrates trust, governance, and runtime transparency.

---

### 9. Desktop technical companion
**As a developer on my machine**, I want a local desktop app that bundles the runtime and gives me a persistent AI shell for project work.

**Prompt example**  
> Open my current workspace and help me continue the last task.

**What Machina does**
- launches as a desktop shell
- restores context
- exposes workspace views and runtime state
- supports local-first operation

**Outcome**  
Machina feels like an always-available technical operating layer, not a disposable browser assistant.

---

## Best-fit sectors

### Primary sector
**Developer Tools / DevEx**

Why this fits:
- workspace-centric
- codebase understanding
- diagnostics
- Git and VS Code integration
- workflows
- operator shell interface

---

### Secondary sector
**Agent orchestration / AI infrastructure**

Why this fits:
- workflows
- agents
- delegation
- approvals
- event-driven execution
- runtime governance

---

### Tertiary sector
**Internal technical automation / AI workspace operations**

Why this fits:
- repeatable technical routines
- governed execution
- operational shell behavior
- inspectable runtime

---

## Practical one-sentence explanation

**Machina helps technical users turn intent into visible, governed execution inside a workspace.**

---

## Strongest first market story

If Machina needs three repeatable headline stories, use these:

### 1. Understand a project in minutes
Repo onboarding and architecture discovery.

### 2. Debug with governed execution
Inspect diagnostics, code, and repo state through one visible workflow.

### 3. Turn technical routines into reusable workflows
Capture repeated engineering tasks as inspectable AI-native execution chains.

These are clear, believable, and aligned with the strongest current shape of the product.

---

## Suggested public wording

### Short pitch
Machina is a local-first AI operating layer for developer workflows.

### Slightly longer pitch
Machina plans, executes, explains, and governs technical actions inside a workspace-aware runtime. It helps developers and technical teams understand projects, debug issues, run repeatable workflows, and coordinate agents with approvals, traceability, and runtime truth.
