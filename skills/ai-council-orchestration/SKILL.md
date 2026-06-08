---
name: ai-council-orchestration
description: Multi-model autonomous loop through Think→Plan→Create→Review→Verify — ALL 14 superpower patterns embedded inline, zero external dependencies. Uses specialized models per stage.
---

# AI Council Orchestration — Multi-Model, Fully Self-Contained

**Everything is built-in.** All 14 superpower patterns are embedded directly in this file. Each stage uses a specialized model plus the relevant embedded pattern. No external Skill calls needed.

## Council Structure

| Agent | Model | Role |
|---|---|---|
| **Thinker** | Claude Opus 4.8 | Deep reasoning, ideation |
| **Planner** | Claude Sonnet 4.6 | Task decomposition |
| **Creator** | GPT-5 or Claude Opus | Implementation + TDD |
| **Critic** | Claude Opus 4.8 | Adversarial review |
| **Reviewer** | Claude Sonnet 4.6 | Code review |
| **Verifier** | Claude Haiku 4.5 (fast) | Final verification |

## Architecture

```
LOOP:
  1. council-orchestrator status          ← check current stage
  2. Switch model to match stage           ← use best model for role
  3. Execute stage with embedded pattern   ← no external Skill calls
  4. GOTO step 1                           ← unconditional

BREAK ONLY when objective met or safety limit hit.
```

## Stage 1 — THINK (Claude Opus 4.8)

**Embedded: Brainstorming Pattern**

1. Switch to Claude Opus 4.8
2. Explore project context.
3. Propose 2-3 architectures with trade-offs.
4. Stress-test assumptions: what could be false?
5. Spawn Thinker sub-agent → `THOUGHT_REPORT.md`
6. Spawn Critic sub-agent → `CRITIQUE_REPORT.md` (adversarial: "assume this is wrong, prove it")
7. If concerns → `council-orchestrator loopback think "<reason>"` → **GOTO LOOP step 1**
8. If clear → `council-orchestrator advance think "approved"` → **GOTO LOOP step 1**

## Stage 2 — PLAN (Claude Sonnet 4.6)

**Embedded: Writing Plans Pattern**

1. Switch to Claude Sonnet 4.6
2. Map every file that will be changed. One responsibility per file.
3. Decompose into bite-sized tasks. Each = one action (2-5 min).
4. Write `TASK_EXECUTION_PLAN.md` with: tasks, files, code in steps, commands, expected output.
5. Self-review: spec coverage? placeholders? type consistency?
6. Spawn Critic: "Any missing success criteria? Dependencies correct?"
7. If concerns → loopback → **GOTO LOOP step 1**
8. If clear → advance → **GOTO LOOP step 1**

## Stage 3 — CREATE (Claude Opus 4.8 or GPT-5)

**Embedded: TDD + Subagent-Driven Development + Parallel Dispatch Patterns**

1. Switch to strongest coding model.
2. For EVERY task, follow strict TDD:
   - **RED:** Write failing test first. No production code without it.
   - **Verify RED:** Watch it fail (right reason — feature missing, not typo).
   - **GREEN:** Minimal code to pass.
   - **Verify GREEN:** Watch it pass. Other tests still pass.
   - **REFACTOR:** Clean up while staying green.
3. Dispatch fresh sub-agents per independent task. Each gets full context (not reading plan file).
4. Two-stage review after each task: spec compliance → code quality.
5. For independent tasks with no shared state: dispatch in parallel.
6. If missing capability → write the pattern as a skill.
7. If done → advance → **GOTO LOOP step 1**
8. If issues → loopback → **GOTO LOOP step 1**

## Stage 4 — REVIEW & TEST (Claude Sonnet 4.6)

**Embedded: Code Review + Systematic Debugging + Verification Patterns**

1. Switch to Claude Sonnet 4.6.
2. Pre-review: get git SHAs, summary of what was built.
3. Spawn ALL council roles to review simultaneously (logic, security, completeness).
4. Evaluate feedback: READ → UNDERSTAND → VERIFY → RESPOND → IMPLEMENT.
5. If flaws found — apply Systematic Debugging:
   - **Phase 1:** Root cause investigation (read errors, reproduce, check changes, trace data flow)
   - **Phase 2:** Pattern analysis (find working examples, compare, identify differences)
   - **Phase 3:** Hypothesis and testing (single hypothesis, minimal test)
   - **Phase 4:** Fix (failing test → single fix → verify → no regressions)
   - **IRON LAW:** No fixes without root cause investigation first.
6. Fix → re-verify → loopback review → **GOTO LOOP step 1**
7. When clean → advance → **GOTO LOOP step 1**

## Stage 5 — VERIFY & DELIVER (Claude Haiku 4.5)

**Embedded: Verification Before Completion + Finishing Branch Patterns**

1. Switch to Claude Haiku 4.5 (fast verification).
2. **IRON LAW:** No "it works" without fresh verification output. Run the FULL command, read the output.
3. Run full test suite, build, integration checks.
4. Spawn completeness verifier: does every requirement from the objective check out?
5. Produce `VERIFICATION_SIGN_OFF.md`.
6. If verified → advance → **GOTO LOOP step 1**
7. If not → loopback to appropriate stage → **GOTO LOOP step 1**

## Delivery Check

- If objective satisfied → DELIVER. **STOP THE LOOP.**
- If not → `council-orchestrator next-iteration` → **GOTO LOOP step 1** (back to Think with learnings)

## Standing Directives

| # | Directive |
|---|---|
| 1 | **NEVER STOP** — no asking for permission. Resolve autonomously. |
| 2 | **GOTO LOOP step 1** — after every action, back to status check. |
| 3 | **TDD always** — no code without failing test first. |
| 4 | **Verify before claiming** — run command, read output, then claim. |
| 5 | **Root cause before fix** — no fixes without investigation. |
| 6 | **Safety limit: 50 iterations** — journal preserved if hit. |

## Activation

1. `council-orchestrator init "<objective>"`
2. **ENTER MAIN LOOP** — `council-orchestrator status`
3. Switch model per stage. Execute with embedded patterns.
4. **GOTO LOOP step 1** after every action.
