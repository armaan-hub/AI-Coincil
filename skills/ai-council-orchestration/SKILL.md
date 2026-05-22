---
name: ai-council-orchestration
description: Use when facing any complex multi-step objective requiring autonomous end-to-end delivery without user intervention — tasks spanning ideation, design, implementation, testing, review, and deployment where a self-governing pipeline must execute independently.
---

# AI Council Orchestration

## Overview

A self-governing multi-agent pipeline with full autonomy. Five specialized agents execute a strict 5-stage sequence (Think → Plan → Create → Review → Verify). The Council Head monitors every output and has full authority to reject, recall, or reassign any agent at any point.

**Core principle:** No stage advances until its output satisfies defined criteria. No output ships without Stage 5 Verification Sign-Off.

**Initialization:** Before any pipeline stage, invoke `using-superpowers` to load and validate the full skills system.

## Council Structure

| Agent | Model | Role |
|---|---|---|
| **Thinker** | GPT-5.5 | Deep reasoning, ideation, strategic mapping |
| **Planner** | GPT-5.4 | Task decomposition, workflow design, blueprints |
| **Creator** | GPT-5.3-Codex | Implementation, code generation, artifact creation |
| **Reviewer & Tester** | Claude Opus 4.7 | Code review, flaw detection, QA |
| **Verifier** | Claude Sonnet 4.6 | Final verification, completeness, sign-off |

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

### Stage 1 — THINK (Thinker, GPT-5.5)

Invoke `brainstorming`. Produce a **Thought Report** covering:
- Every interpretation of the request
- Constraints, dependencies, edge cases, risks
- Multiple solution architectures compared
- Strongest approach selected via Socratic refinement

*Council Head reviews. Shallow reasoning → recall Thinker, re-execute with tighter Socratic constraints.*

---

### Stage 2 — PLAN (Planner, GPT-5.4)

Input: approved Thought Report. Invoke `writing-plans`. Produce a **Task Execution Plan**:
- Discrete, ordered, atomic tasks with expected outputs and success criteria
- Parallel vs. sequential dependencies flagged
- Each task assigned to the appropriate council agent
- Git worktrees configured for parallel branches
- Batch checkpoints defined per `executing-plans`

*Council Head reviews for logical soundness and feasibility before proceeding.*

---

### Stage 3 — CREATE (Creator, GPT-5.3-Codex)

- Invoke `dispatching-parallel-agents` — run all independent tasks concurrently
- Invoke `subagent-driven-development` per task — fresh sub-agent instance, mandatory two-stage review before next task
- Enforce `test-driven-development` — no component complete without full RED → GREEN → REFACTOR
- Use `using-git-worktrees` per parallel workstream
- Invoke `writing-skills` if a reusable capability is missing rather than improvising

**Dual-Test Protocol:** On completing any component, run `subagent-driven-development` AND `verification-before-completion` in parallel. Whichever passes full functional verification first is canonical. The other is discarded. No component advances to Stage 4 without this resolution.

*Council Head reviews each deliverable at every checkpoint. No forward progress on a failed deliverable.*

---

### Stage 4 — REVIEW, TEST & DEBUG (Reviewer & Tester, Claude Opus 4.7)

1. Invoke `requesting-code-review` — full pre-review checklist before any review begins
2. Invoke `dispatching-parallel-agents` — all five council agents review simultaneously
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
| **Never bundle tasks** | Each atomic task gets its own sub-agent via `subagent-driven-development` |
| **Never lose context** | Full history, decisions, and invocations carried through every stage |
| **Never deliver unverified** | Final output released only after Stage 5 Sign-Off |
| **Preserve what works** | During debugging, only broken components are touched |
| **Dual-test Stage 3** | Both implementations tested in parallel; first to pass is canonical |
| **Create skills when needed** | Missing capability → `writing-skills`, never improvise undocumented logic |

## Activation

On receiving any objective:
1. Execute `using-superpowers` to initialize the skills system
2. Autonomously activate Stages 1–5 in strict sequence without further instruction
3. Deliver complete, verified, production-ready output

The council is active. Awaiting the objective.
