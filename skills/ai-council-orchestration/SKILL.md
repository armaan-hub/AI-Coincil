---
name: ai-council-orchestration
description: Multi-model autonomous loop through Think→Plan→Create→Review→Verify — uses specialized models per stage. Loops until objective is fully resolved.
---

# AI Council Orchestration — Multi-Model Autonomous Loop

## Overview

The **multi-model variant** of the council orchestration. Same autoresearch-style loop, but each stage uses a **different specialized model** for optimal results.

**Inspired by Karpathy's autoresearch:** the loop runs autonomously forever. Each iteration is self-contained. The loop keeps turning until objective is met or safety limit is hit.

## Council Structure

| Agent | Recommended Model | Role |
|---|---|---|
| **Thinker** | Claude Opus 4.8 | Deep reasoning, ideation, strategic mapping |
| **Planner** | Claude Sonnet 4.6 | Task decomposition, workflow design |
| **Creator** | GPT-5 or Claude Opus | Implementation, code generation |
| **Critic** | Claude Opus 4.8 | Adversarial review, stress-testing |
| **Reviewer** | Claude Sonnet 4.6 | Code review, flaw detection, QA |
| **Verifier** | Claude Haiku 4.5 (fast) | Final verification, completeness check |

## Superpowers Integration

| Stage | Skill Invocations |
|---|---|
| **Init** | `Skill(skill="using-superpowers")` |
| **1 — Think** | `Skill(skill="superpowers:brainstorming")`, spawn Thinker + Critic |
| **2 — Plan** | `Skill(skill="superpowers:writing-plans")`, `Skill(skill="superpowers:executing-plans")`, `Skill(skill="superpowers:using-git-worktrees")`, spawn Planner + Critic |
| **3 — Create** | `Skill(skill="superpowers:dispatching-parallel-agents")`, `Skill(skill="superpowers:subagent-driven-development")`, `Skill(skill="superpowers:test-driven-development")`, `Skill(skill="superpowers:writing-skills")` |
| **4 — Review & Test** | `Skill(skill="code-review:code-review")`, `Skill(skill="superpowers:requesting-code-review")`, `Skill(skill="superpowers:receiving-code-review")`, `Skill(skill="superpowers:systematic-debugging")`, `Skill(skill="superpowers:verification-before-completion")` |
| **5 — Verify & Deliver** | `Skill(skill="superpowers:verification-before-completion")`, `Skill(skill="superpowers:finishing-a-development-branch")` |

## Architecture

```
MAIN LOOP (autonomous, never stop):

LOOP:
  1. council-orchestrator status          ← check current stage
  2. Switch model to match the stage       ← use best model for the role
  3. Execute the stage handler             ← with superpowers skill invocations
  4. council-orchestrator status          ← verify transition
  5. GOTO step 1                           ← unconditional, never ask permission

  Stage 1 — THINK     → model: Claude Opus 4.8 → brainstorming + Thinker + Critic
  Stage 2 — PLAN      → model: Claude Sonnet 4.6 → writing-plans + executing-plans + git-worktrees + Planner + Critic
  Stage 3 — CREATE    → model: Opus 4.8 or GPT-5 → parallel agents + TDD + Critic
  Stage 4 — REVIEW    → model: Claude Sonnet 4.6 → code-review:code-review + debugging + verification
  Stage 5 — VERIFY    → model: Haiku 4.5 → verification-before-completion + finishing-a-development-branch
  DELIVERY CHECK      → if objective met → deliver | if not → next-iteration → GOTO step 1
```

## State Management

Uses `council_journal.md` and `council-orchestrator` identically to council-orchestration.

```bash
council-orchestrator init "<objective>"
council-orchestrator status               # Check current stage
council-orchestrator advance <stage>      # Mark complete
council-orchestrator loopback <stage> "reason"  # Go back
council-orchestrator next-iteration       # Start new iteration
```

## 5-Stage Pipeline

### Stage 1 — THINK (Claude Opus 4.8)

1. Switch model to Claude Opus 4.8
2. `Skill(skill="superpowers:brainstorming", args="<objective>")` — Socratic ideation
3. Spawn Thinker sub-agent → produce THOUGHT_REPORT.md
4. Spawn Critic sub-agent in parallel → produce CRITIQUE_REPORT.md
5. If concerns → `council-orchestrator loopback think "<reason>"` → recall Thinker → **GOTO MAIN LOOP step 1**
6. If clear → `council-orchestrator advance think "approved"` → **GOTO MAIN LOOP step 1**

### Stage 2 — PLAN (Claude Sonnet 4.6)

1. Switch model to Claude Sonnet 4.6
2. `Skill(skill="superpowers:writing-plans", args="Plan: <objective>")`
3. `Skill(skill="superpowers:executing-plans", args="Set up batch checkpoints")`
4. `Skill(skill="superpowers:using-git-worktrees", args="Configure parallel branches")`
5. Spawn Planner sub-agent → TASK_EXECUTION_PLAN.md
6. Spawn Critic in parallel → PLAN_CRITIQUE.md
7. If concerns → loopback → recall Planner → **GOTO MAIN LOOP step 1**
8. If clear → advance → **GOTO MAIN LOOP step 1**

### Stage 3 — CREATE (Claude Opus 4.8 or GPT-5)

1. Switch to strongest coding model
2. Invoke dispatching-parallel-agents, subagent-driven-development, test-driven-development
3. Critic per component
4. Dual-test protocol
5. If issues → loopback → fix → retry → **GOTO MAIN LOOP step 1**
6. If clear → advance → **GOTO MAIN LOOP step 1**

### Stage 4 — REVIEW & TEST (Claude Sonnet 4.6)

1. Switch to Claude Sonnet 4.6
2. `Skill(skill="superpowers:requesting-code-review", args="Pre-review checklist")`
3. `Skill(skill="code-review:code-review", args="Review all code for correctness")`
4. `Skill(skill="superpowers:receiving-code-review", args="Process feedback")`
5. All council roles review simultaneously
6. If flaws → `Skill(skill="superpowers:systematic-debugging")` → fix → `Skill(skill="superpowers:verification-before-completion")` → re-review → **GOTO MAIN LOOP step 1**
7. Loop until zero unresolved issues
8. Advance → **GOTO MAIN LOOP step 1**

### Stage 5 — VERIFY & DELIVER (Claude Haiku 4.5)

1. Switch to Claude Haiku 4.5 (fast, cheap verification)
2. `Skill(skill="superpowers:verification-before-completion", args="End-to-end verification")`
3. `Skill(skill="superpowers:finishing-a-development-branch", args="Merge and finalize")`
4. Produce VERIFICATION_SIGN_OFF.md
5. If verified → `council-orchestrator advance verify "passed"` → **GOTO MAIN LOOP step 1**
6. If not → loopback to fix → **GOTO MAIN LOOP step 1**

### Delivery Check

If `council-orchestrator status` shows `stage: __delivery_check__`:

- If objective fully satisfied → DELIVER final output → **STOP THE LOOP**
- If not → `council-orchestrator next-iteration` → loop back to Stage 1 → **GOTO MAIN LOOP step 1**

## Standing Directives

| # | Directive |
|---|---|
| 1 | **NEVER STOP** — no pausing for approval. Resolve blockers autonomously |
| 2 | **GOTO MAIN LOOP step 1** — after every action, immediately go back to status check |
| 3 | **Switch model per stage** — use the best model for each role |
| 4 | **Always check state first** — `council-orchestrator status` before acting |
| 5 | **Never skip review** — every stage output reviewed |
| 6 | **Never silence the Critic** — explicit "no concerns" if none |
| 7 | **Correct skill names** — `code-review:code-review`, not `superpowers:code-review` |
| 8 | **Safety limit: 50 iterations** — journal preserved if hit |
| 9 | **Auto-compact at 140K tokens** — run /compact, resume from journal |
| 10 | **Dual-test Stage 3** — both implementations tested; first to pass is canonical |

## Activation

1. `Skill(skill="using-superpowers")` — load skills system
2. `council-orchestrator init "<objective>"`
3. Switch model per stage using available method
4. **ENTER MAIN LOOP** — start with `council-orchestrator status`
5. After every stage, **GOTO step 4**
6. NEVER STOP until objective is met
