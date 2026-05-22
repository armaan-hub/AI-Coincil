---
name: council-orchestration
description: Use when facing any complex multi-step objective requiring autonomous end-to-end delivery without user intervention, where all orchestration must run on the current active model without switching models between agents.
---

# Council Orchestration (Universal / Single-Model)

## Overview

A self-governing 5-stage multi-agent pipeline that runs entirely on **the current active model** — no model switching, no external API dependencies. Works identically in Claude Code, Copilot CLI, Codex, and any other agent CLI.

**Core principle:** Every council agent is a sub-agent instance of the same model you're already using. The Council Head (you) orchestrates, monitors, and has full authority to reject, recall, or reassign any sub-agent at any stage.

**Initialization:** Before any pipeline stage, invoke `using-superpowers` to load and validate the full skills system.

## Council Structure

All five roles run on the **current active model**. The model does NOT change between agents.

| Role | Responsibility |
|---|---|
| **Thinker** | Deep reasoning, ideation, assumption stress-testing |
| **Planner** | Task decomposition, workflow design, blueprints |
| **Creator** | Implementation, code generation, artifact creation |
| **Reviewer & Tester** | Code review, flaw detection, quality assurance |
| **Verifier** | Final verification, completeness check, sign-off |

> **Dispatch pattern:** Use `dispatching-parallel-agents` or `subagent-driven-development` to spin up sub-agents. Each sub-agent inherits the current model automatically — no model param needed.

## Superpowers Registry

| Stage | Superpower | Function |
|---|---|---|
| Init | `using-superpowers` | Initialize skills system |
| 1 | `brainstorming` | Socratic ideation, stress-test assumptions |
| 2 | `writing-plans` | Structured implementation blueprint |
| 2 | `executing-plans` | Batch task execution with checkpoints |
| 2 | `using-git-worktrees` | Isolate parallel development branches |
| 3 | `dispatching-parallel-agents` | Concurrent sub-agent workflows |
| 3 | `subagent-driven-development` | Per-task sub-agent, two-stage review |
| 3 | `test-driven-development` | RED → GREEN → REFACTOR on every component |
| 3 | `writing-skills` | Create missing reusable capabilities |
| 4 | `requesting-code-review` | Pre-review checklist |
| 4 | `receiving-code-review` | Structured feedback response protocol |
| 4 | `systematic-debugging` | 4-phase root cause diagnosis |
| 4 | `verification-before-completion` | Confirm fixes are functional |
| 5 | `verification-before-completion` | End-to-end completeness check |
| 5 | `finishing-a-development-branch` | Merge and PR decision workflow |

## 5-Stage Pipeline

### Stage 1 — THINK (Thinker sub-agent)

Invoke `brainstorming`. Produce a **Thought Report**:
- Every interpretation of the request
- Constraints, dependencies, edge cases, risks
- Multiple solution architectures compared
- Strongest approach via Socratic refinement

*Council Head reviews. Shallow reasoning → recall, re-execute with tighter constraints.*

---

### Stage 2 — PLAN (Planner sub-agent)

Input: approved Thought Report. Invoke `writing-plans`. Produce **Task Execution Plan**:
- Discrete, ordered, atomic tasks with success criteria
- Parallel vs. sequential dependencies flagged
- Each task assigned to appropriate council role
- Git worktrees configured for parallel branches
- Batch checkpoints per `executing-plans`

*Council Head reviews for soundness before proceeding.*

---

### Stage 3 — CREATE (Creator sub-agent + parallel support)

- Invoke `dispatching-parallel-agents` — run independent tasks concurrently
- Invoke `subagent-driven-development` per task — fresh sub-agent, mandatory two-stage review before next task
- Enforce `test-driven-development` — no component complete without RED → GREEN → REFACTOR
- Use `using-git-worktrees` per parallel workstream
- Invoke `writing-skills` if a reusable capability is missing

**Dual-Test Protocol:** On completing any component, run `subagent-driven-development` AND `verification-before-completion` in parallel. First to pass full verification is canonical; the other is discarded. No component advances to Stage 4 without this.

*Council Head reviews at every checkpoint. No forward progress on failed deliverables.*

---

### Stage 4 — REVIEW, TEST & DEBUG (Reviewer sub-agent + full council)

1. Invoke `requesting-code-review` — pre-review checklist before any review begins
2. Invoke `dispatching-parallel-agents` — all five council roles review simultaneously
3. Each reviews: logic errors, inefficiencies, security gaps, anti-patterns, integration failures, objective deviation
4. Invoke `receiving-code-review` — no feedback dismissed without documented reasoning
5. Re-enforce `test-driven-development` — retest all components post-review
6. Produce **Review & Issue Report**

**If any flaw detected:**
- Invoke `systematic-debugging` — 4-phase root cause diagnosis
- Recall responsible sub-agent; fix in isolation; never touch working components
- Invoke `verification-before-completion` to confirm fix before resuming
- Loop until Report returns zero unresolved issues

*No output leaves Stage 4 with unresolved issues.*

---

### Stage 5 — VERIFY & DELIVER (Verifier sub-agent)

- Invoke `verification-before-completion` — confirm every component is functional as an integrated whole
- Confirm output satisfies original objective — nothing missing, nothing broken
- Invoke `finishing-a-development-branch` — merge/PR workflow, resolve all branch conflicts
- Produce **Verification Sign-Off Report**

*Council Head releases final output only upon successful Sign-Off.*

---

## Standing Directives

| Directive | Rule |
|---|---|
| **Never halt** | No stage waits for user input; blockers resolved autonomously |
| **Never skip review** | Every stage output reviewed by Council Head before advancing |
| **Never bundle tasks** | Each atomic task gets its own sub-agent |
| **Never lose context** | Full history and decisions carried through every stage |
| **Never deliver unverified** | Final output only after Stage 5 Sign-Off |
| **Preserve what works** | During debugging, only broken components are touched |
| **Dual-test Stage 3** | Both implementations tested in parallel; first to pass is canonical |
| **Create skills when needed** | Missing capability → `writing-skills`, never improvise |
| **Never switch models** | All sub-agents inherit the current active model — no overrides |

## Installation

### Claude Code
```bash
cp -r council-orchestration ~/.claude/skills/
```

### Copilot CLI (superpowers)
```bash
cp -r council-orchestration \
  ~/.copilot/installed-plugins/superpowers-marketplace/superpowers/skills/
```

### Invoke
```
Use the skill tool to invoke "council-orchestration"
```

## Activation

On receiving any objective:
1. Execute `using-superpowers` to initialize the skills system
2. Autonomously activate Stages 1–5 in strict sequence
3. Deliver complete, verified, production-ready output

The council is active on the current model. Awaiting the objective.
