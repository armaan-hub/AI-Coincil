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

## Architecture

Identical loop structure to `council-orchestration` but with model switching per stage:

```
MAIN LOOP (autonomous, never stop):
  Stage 1 — THINK     → Switch model to Claude Opus 4.8 → invoke brainstorming + Thinker + Critic
  Stage 2 — PLAN      → Switch model to Claude Sonnet 4.6 → invoke writing-plans + Planner + Critic
  Stage 3 — CREATE    → Switch model to Opus 4.8 or GPT-5 → invoke parallel agents + TDD + Critic
  Stage 4 — REVIEW    → Switch model to Claude Sonnet 4.6 → invoke code-review + debugging
  Stage 5 — VERIFY    → Switch model to Haiku 4.5 → invoke verification + finishing
  DELIVERY CHECK      → If objective met → deliver. If not → loop back to Stage 1 with learnings
```

## State Management

Uses `council_journal.md` and `orchestrator.py` identically to council-orchestration.

```bash
python orchestrator.py init "<objective>"
python orchestrator.py status      # Check current stage
python orchestrator.py advance <stage>  # Mark complete
python orchestrator.py loopback <stage> "reason"  # Go back
python orchestrator.py next-iteration  # Start new iteration
```

## 5-Stage Pipeline

### Stage 1 — THINK (Claude Opus 4.8)

1. Switch model to Claude Opus 4.8 using `/switch-model` or `Skill(skill="switch-model", args="claude-opus-4-8")`
2. `Skill(skill="superpowers:brainstorming", args="<objective>")` — Socratic ideation
3. Spawn Thinker sub-agent to produce THOUGHT_REPORT.md
4. Spawn Critic sub-agent in parallel to produce CRITIQUE_REPORT.md
5. If concerns → `python orchestrator.py loopback think "<reason>"` → recall Thinker
6. If clear → `python orchestrator.py advance think "approved"`

### Stage 2 — PLAN (Claude Sonnet 4.6)

1. Switch model to Claude Sonnet 4.6
2. `Skill(skill="superpowers:writing-plans", args="Plan: <objective>")`
3. Spawn Planner sub-agent → TASK_EXECUTION_PLAN.md
4. Spawn Critic in parallel → PLAN_CRITIQUE.md
5. If concerns → loopback → recall Planner
6. If clear → advance

### Stage 3 — CREATE (Claude Opus 4.8 or GPT-5)

1. Switch to strongest coding model
2. Invoke dispatching-parallel-agents, subagent-driven-development, test-driven-development
3. Critic per component
4. Dual-test protocol
5. If issues → loopback → fix → retry
6. If clear → advance

### Stage 4 — REVIEW & TEST (Claude Sonnet 4.6)

1. Switch to Claude Sonnet 4.6
2. Invoke code-review, receiving-code-review
3. All council roles review simultaneously
4. If flaws → systematic-debugging → fix → verification → re-review
5. Loop until zero unresolved issues
6. Advance

### Stage 5 — VERIFY & DELIVER (Claude Haiku 4.5)

1. Switch to Claude Haiku 4.5 (fast, cheap verification)
2. Invoke verification-before-completion
3. Produce VERIFICATION_SIGN_OFF.md
4. If verified → advance to delivery check
5. If not → loopback to Stage 3 (or appropriate stage)

### Delivery Check

- If objective fully satisfied → DELIVER final output
- If not → `python orchestrator.py next-iteration` → loop back to Stage 1 with learnings

## Standing Directives

| # | Directive |
|---|---|
| 1 | **NEVER STOP** — no pausing for approval. Resolve blockers autonomously |
| 2 | **Switch model per stage** — use the best model for each role |
| 3 | **Always check state first** — `python orchestrator.py status` before acting |
| 4 | **Never skip review** — every stage output reviewed |
| 5 | **Never silence the Critic** — explicit "no concerns" if none |
| 6 | **Safety limit: 50 iterations** — journal preserved if hit |
| 7 | **Auto-compact at 140K tokens** — run /compact, resume from journal |
| 8 | **Dual-test Stage 3** — both implementations tested; first to pass is canonical |

## Activation

1. `Skill(skill="using-superpowers")` — load skills system
2. `python orchestrator.py init "<objective>"`
3. Switch model per stage using skill or /switch-model
4. Execute stage with superpowers integration
5. Advance or loopback based on results
6. NEVER STOP until objective is met
