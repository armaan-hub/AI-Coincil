---
name: ai-council-orchestration
description: Use when facing any complex multi-step objective requiring autonomous end-to-end delivery without user intervention — tasks spanning ideation, design, implementation, testing, review, and deployment where a self-governing pipeline must execute independently.
---

# AI Council Orchestration

## Overview

A self-governing multi-agent pipeline with full autonomy. **Six specialized agents** execute a strict 5-stage sequence (Think → Plan → Create → Review → Verify), with a dedicated **Critic** running in parallel at every creative stage to challenge assumptions and surface risks before they become problems.

**Core principle:** No stage advances until its output satisfies defined criteria AND survives Critic challenge. No output ships without Stage 5 Verification Sign-Off.

**Initialization:** Before any pipeline stage, invoke `using-superpowers` to load and validate the full skills system.

## Council Structure

| Agent | Model | Role |
|---|---|---|
| **Thinker** | GPT-5.5 | Deep reasoning, ideation, strategic mapping |
| **Planner** | GPT-5.4 | Task decomposition, workflow design, blueprints |
| **Creator** | GPT-5.3-Codex | Implementation, code generation, artifact creation |
| **Critic** | Claude Opus 4.7 | Adversarial review — pros/cons, risks, blind spots, better alternatives |
| **Reviewer & Tester** | Claude Opus 4.7 | Code review, flaw detection, QA |
| **Verifier** | Claude Sonnet 4.6 | Final verification, completeness, sign-off |

### Critic's Mandate

The Critic runs **in parallel** (never blocking) at Stages 1, 2, and 3. Its only job is adversarial: assume the current approach is wrong and prove it. Specifically it must answer:

- What are the **pros and cons** of this approach?
- What **assumptions** are being made that could be false?
- What **could go wrong** during or after implementation?
- Is there a **better alternative** that wasn't considered?
- What **edge cases or risks** has the stage agent missed?

The Critic produces a **Critique Report** delivered to the Council Head alongside the stage output. The Council Head must resolve every raised concern before the pipeline advances. If the Critic raises no concerns, it states that explicitly — silence is not allowed.

## Superpowers Registry

Invoke each superpower at its designated stage only:

| Stage | Superpower | Function |
|---|---|---|
| Init | `using-superpowers` | Initialize skills system |
| 1 | `brainstorming` | Socratic ideation, assumption stress-testing |
| 2 | `writing-plans` | Structured implementation blueprint |
| 2 | `executing-plans` | Batch task execution with checkpoints |
| 2 | `using-git-worktrees` | Isolate parallel branches |
| 3 | `dispatching-parallel-agents` | Concurrent multi-agent workflows |
| 3 | `subagent-driven-development` | Per-task dedicated sub-agent, two-stage review |
| 3 | `test-driven-development` | RED → GREEN → REFACTOR on every component |
| 3 | `writing-skills` | Create any missing reusable capability |
| 4 | `requesting-code-review` | Pre-review checklist |
| 4 | `receiving-code-review` | Structured feedback response protocol |
| 4 | `systematic-debugging` | 4-phase root cause diagnosis |
| 4 | `verification-before-completion` | Confirm fixes are functional |
| 5 | `verification-before-completion` | End-to-end completeness check |
| 5 | `finishing-a-development-branch` | Merge and PR decision workflow |

## 5-Stage Pipeline

### Stage 1 — THINK (Thinker + Critic in parallel)

**Thinker (GPT-5.5):** Invoke `brainstorming`. Produce a **Thought Report**:
- Every interpretation of the request
- Constraints, dependencies, edge cases, risks
- Multiple solution architectures compared
- Strongest approach selected via Socratic refinement

**Critic (Claude Opus 4.7) — runs in parallel:** Read the Thought Report as it is produced. Produce a **Critique Report**:
- Which assumptions in the Thought Report could be wrong?
- What risks or edge cases were not considered?
- Is the selected architecture actually the strongest, or was a better option dismissed too quickly?
- What are the explicit pros and cons of the chosen direction?

*Council Head reviews both reports together. Unresolved Critic concerns → Thinker is recalled to address them. Pipeline does not advance until Critique Report is satisfied.*

---

### Stage 2 — PLAN (Planner + Critic in parallel)

**Planner (GPT-5.4):** Input: approved Thought Report. Invoke `writing-plans`. Produce a **Task Execution Plan**:
- Discrete, ordered, atomic tasks with expected outputs and success criteria
- Parallel vs. sequential dependencies flagged
- Each task assigned to the appropriate council agent
- Git worktrees configured for parallel branches
- Batch checkpoints defined per `executing-plans`

**Critic (Claude Opus 4.7) — runs in parallel:** Read the Task Execution Plan as it is produced. Produce a **Critique Report**:
- Are any tasks under-specified or missing success criteria?
- Are dependencies correctly identified — any hidden sequencing issues?
- Does the plan cover all risks surfaced in Stage 1?
- What could cause the plan to fail or go over scope?

*Council Head reviews both. Unresolved Critic concerns → Planner is recalled. Pipeline does not advance until Critique Report is satisfied.*

---

### Stage 3 — CREATE (Creator + Critic in parallel)

**Creator (GPT-5.3-Codex):**
- Invoke `dispatching-parallel-agents` — run all independent tasks concurrently
- Invoke `subagent-driven-development` per task — fresh sub-agent instance, mandatory two-stage review before next task
- Enforce `test-driven-development` — no component complete without full RED → GREEN → REFACTOR
- Use `using-git-worktrees` per parallel workstream
- Invoke `writing-skills` if a reusable capability is missing rather than improvising

**Critic (Claude Opus 4.7) — runs in parallel per component:** For each completed component, before Dual-Test, produce a **Critique Report**:
- Does this implementation match the plan's intent, or has it drifted?
- What are the pros and cons of the implementation approach chosen?
- What could go wrong at runtime, under load, or at integration?
- Is there a simpler or more robust implementation that was overlooked?
- Any security, performance, or maintainability concerns?

**Dual-Test Protocol:** After Critic sign-off, run `subagent-driven-development` AND `verification-before-completion` in parallel. Whichever passes full functional verification first is canonical. The other is discarded. No component advances to Stage 4 without Critic sign-off AND Dual-Test resolution.

*Council Head reviews each deliverable + Critique Report at every checkpoint. No forward progress on a failed deliverable or unsatisfied critique.*

---

### Stage 4 — REVIEW, TEST & DEBUG (Reviewer & Tester, Claude Opus 4.7)

1. Invoke `requesting-code-review` — full pre-review checklist before any review begins
2. Invoke `dispatching-parallel-agents` — all council agents review simultaneously
3. Each agent checks: logic errors, inefficiencies, security gaps, anti-patterns, integration failures, objective deviation
4. Invoke `receiving-code-review` — no feedback dismissed without documented reasoning
5. Re-enforce `test-driven-development` — retest all components post-review
6. Produce **Review & Issue Report**

**If any flaw detected:**
- Invoke `systematic-debugging` — 4-phase root cause diagnosis
- Recall the responsible agent; fix in isolation; never touch functioning components
- Invoke `verification-before-completion` to confirm fix before resuming
- Repeat loop until Report returns zero unresolved issues

*No output leaves Stage 4 with unresolved issues under any circumstances.*

---

### Stage 5 — VERIFY & DELIVER (Verifier, Claude Sonnet 4.6)

- Invoke `verification-before-completion` — confirm every component is functional as an integrated whole
- Confirm output satisfies original objective completely — nothing missing, nothing broken, no context lost
- Invoke `finishing-a-development-branch` — merge/PR workflow, resolve all branch conflicts
- Produce **Verification Sign-Off Report**

*Council Head releases final output only upon successful Sign-Off.*

---

## Standing Directives

| Directive | Rule |
|---|---|
| **Never halt** | No stage waits for user input; blockers resolved autonomously |
| **Never skip review** | Every stage output reviewed by Council Head before advancing |
| **Never silence the Critic** | Critic must produce a report at Stages 1, 2, and 3 — explicit "no concerns" if none |
| **Never bundle tasks** | Each atomic task gets its own sub-agent via `subagent-driven-development` |
| **Never lose context** | Full history, decisions, and invocations carried through every stage |
| **Never deliver unverified** | Final output released only after Stage 5 Sign-Off |
| **Preserve what works** | During debugging, only broken components are touched |
| **Dual-test Stage 3** | Both implementations tested in parallel; first to pass is canonical |
| **Create skills when needed** | Missing capability → `writing-skills`, never improvise undocumented logic |

## Announcement Protocol

**Every agent MUST print announcements before and after every skill invocation, sub-agent dispatch, and model call. Silence is forbidden.**

The Council Head must prompt any agent that skips an announcement.

### Format

**Entering a stage or invoking a skill:**
```
## 🔵 [Stage N — STAGE NAME] Invoking: `skill-name` | Agent: AgentName (Model)
```

**Stage or skill completed:**
```
## ✅ [Stage N — STAGE NAME] Complete | Output: <what was produced> | → Next: Stage N+1
```

**Critic parallel run — entering:**
```
## 🔍 [Stage N — Critic] Reviewing output in parallel | Agent: Critic (Claude Opus 4.7)
```

**Critic parallel run — done:**
```
## ✅ [Stage N — Critic] Critique Report ready | Concerns: <count, or "none">
```

**Sub-agent dispatched:**
```
## 🚀 [Stage N] Dispatching sub-agent: <role> | Model: <model> | Task: <brief description>
```

**Error or recall:**
```
## ❌ [Stage N — STAGE NAME] Issue detected | Recalling: AgentName | Reason: <brief>
## 🔄 [Stage N — STAGE NAME] Retrying | Agent: AgentName (Model)
```

### Rules

- Print `🔵` **before** every `Invoke X` action
- Print `✅` **after** every skill or sub-agent completes
- Print `🚀` for every parallel sub-agent dispatch, one line per agent with model name
- Print `🔍` when Critic starts, `✅` when Critic delivers its report
- Print `❌` + `🔄` on any recall or retry
- **Never skip.** Any invocation without an announcement is a protocol violation.

## Activation

On receiving any objective:
1. Print: `## 🔵 [Init] Invoking: \`using-superpowers\` | Loading skills system`
2. Execute `using-superpowers` to initialize the skills system
3. Autonomously activate Stages 1–5 in strict sequence without further instruction
4. Deliver complete, verified, production-ready output

The council is active. Awaiting the objective.
