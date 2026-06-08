---
name: council-orchestration
description: Fully self-contained autonomous autoresearch loop — Think→Plan→Create→Review→Verify, iterates until objective satisfied. ALL superpower skills embedded inline, zero external dependencies. Includes live model discovery.
---

# Council Orchestration — Fully Self-Contained Autonomous Loop

**Everything is built-in.** All 14 superpower patterns are embedded directly in this file. No external Skill calls needed. The council reads, applies, and loops autonomously until the objective is met.

**Model reference:** All available models via proxy can be discovered live with `council-orchestrator models`.

---

## Architecture

```
MAIN LOOP (autonomous, never stop):

LOOP:
  1. council-orchestrator status          ← check current stage
  2. Execute the stage handler            ← uses embedded patterns below
  3. council-orchestrator status          ← verify transition
  4. GOTO step 1                          ← UNCONDITIONAL

BREAK ONLY when:
  - Delivery check says objective satisfied → DELIVER
  - __maxed_out__ safety limit → REPORT

  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌──────────┐   ┌──────────┐
  │ THINK   │ → │ PLAN    │ → │ CREATE  │ → │ REVIEW   │ → │ VERIFY   │
  │ +CRITIC │   │ +CRITIC │   │ +CRITIC │   │ & TEST   │   │ & DELIVER│
  └────┬────┘   └────┬────┘   └────┬────┘   └────┬─────┘   └────┬─────┘
       │             │             │             │              │
       ◄─────────────┴─────────────┴─────────────┴──────────────┘
       │   loop back via loopback if patterns detect issues       │
       └──────────────────────────────────────────────────────────┘
                     │  if !satisfied → next-iteration → GOTO top
                     └──────────────────────────────────────────┘
```

---

## State Management

```bash
council-orchestrator init "<objective>"          # Start
council-orchestrator status                      # Current stage
council-orchestrator advance <stage>             # Mark done
council-orchestrator loopback <stage> "reason"   # Go back
council-orchestrator next-iteration              # New iteration
council-orchestrator models                      # Discover live model catalog
```

---

## Model Reference

**Before starting a council session, run:**
```bash
council-orchestrator models
```
This writes `COUNCIL_MODELS.md` with all models available via your AI proxy at `http://127.0.0.1:4001`.

### Fallback catalog (when proxy unreachable)

**If you have GitHub Copilot connected:**
- Thinker/Critic → claude-opus-4.6-1m (strongest)
- Planner/Reviewer → claude-sonnet-4.6 (balanced)
- Creator → gpt-5.4 or gpt-5.2
- Verifier → claude-haiku-4.5 (cheapest) or gpt-5-mini (FREE)

**If only OpenCode Zen:**
- Thinker/Critic → deepseek-v4-pro, qwen3.7-max, kimi-k2.6
- Planner/Reviewer → qwen3.6-plus, minimax-m2.7
- Creator → deepseek-v4-flash, minimax-m2.7
- Verifier → deepseek-v4-flash-free (FREE) or any free model

**For multi-model orchestration,** use the sibling skill `ai-council-orchestration` which switches models per-stage.

---

## The Main Loop

```
LOOP:
  1. Run: council-orchestrator status
  2. Match the "Stage:" field:
     "think"             → execute Stage 1 — THINK
     "plan"              → execute Stage 2 — PLAN
     "create"            → execute Stage 3 — CREATE
     "review"            → execute Stage 4 — REVIEW & TEST
     "verify"            → execute Stage 5 — VERIFY & DELIVER
     "__delivery_check__"→ run DELIVERY CHECK
     "__maxed_out__"     → print summary, STOP
  3. After handler finishes → IMMEDIATELY GOTO step 1
```

---

## Stage 1 — THINK

### Uses Embedded: Brainstorming Pattern + Critic Pattern

**Announce:** `## 💭 [Stage 1 — THINK] Using Brainstorming Pattern`

### Step 1: Explore Context
Check project files, docs, recent commits. Understand what exists.

### Step 2: Clarify & Decompose
Break down the objective. Identify independent subsystems. If too large, decompose into sub-projects — each gets its own Think→Plan→Create cycle.

### Step 3: Propose 2-3 Architectures
Compare approaches with explicit trade-offs. Cover:
- Architecture & components
- Data flow & interfaces
- Error handling & edge cases
- Testing strategy

### Step 4: Socratic Refinement
For the recommended approach, stress-test:
- **What assumptions are you making?** Could they be false?
- **What constraints are non-negotiable?**
- **What could go wrong?**

### Step 5: Produce Thought Report
Write `THOUGHT_REPORT.md` with: interpretations, constraints, risk analysis, 3+ architectures compared (pros/cons), recommended approach with justification.

### Step 6: Apply Critic Pattern
**Spawn Critic sub-agent** with mandate:
> "Assume the current approach is wrong. What assumptions could be false? What risks were missed? Is the selected architecture actually strongest? What pros/cons were downplayed?"
> Produce `CRITIQUE_REPORT.md`. If no concerns, state EXACTLY: "No concerns — approach is sound."

### Step 7: Resolve or Advance
- Critic has concerns → `council-orchestrator loopback think "<reason>"` → recall Thinker → **GOTO LOOP step 1**
- No concerns → `council-orchestrator advance think "approved"` → **GOTO LOOP step 1**

---

## Stage 2 — PLAN

### Uses Embedded: Writing Plans Pattern + Git Worktrees Pattern

**Announce:** `## 📋 [Stage 2 — PLAN] Using Writing Plans Pattern`

### Step 1: Map File Structure
Before tasks, map every file that will be created/modified. Each file = one clear responsibility. Follow existing codebase patterns.

### Step 2: Decompose into Bite-Sized Tasks
Each task = one action (2-5 minutes):
```
Task 1: Write failing test
Task 2: Run to confirm failure
Task 3: Implement minimal code
Task 4: Run to confirm pass
Task 5: Commit
```

### Step 3: Write Plan
Write `TASK_EXECUTION_PLAN.md` with:
- **Goal:** One sentence
- **Architecture:** 2-3 sentences
- **Tech Stack:** Key technologies
- **Tasks:** Each with: files touched, exact file paths, code in steps, expected output, exact commands

### Step 4: Self-Review Plan
Check:
- ✅ Spec coverage — every requirement maps to a task
- ✅ No placeholders ("TBD", "TODO", "implement later")
- ✅ Type consistency — function signatures match across tasks
- ✅ Actual code in every step, not descriptions

### Step 5: Apply Critic Pattern
Spawn Critic: "Are any tasks under-specified? Dependencies correct? Risks from Stage 1 covered?"

### Step 6: Resolve or Advance
- Concerns → `council-orchestrator loopback plan "<reason>"` → **GOTO LOOP step 1**
- Clear → `council-orchestrator advance plan "approved"` → **GOTO LOOP step 1**

---

## Stage 3 — CREATE

### Uses Embedded: TDD Pattern + Subagent-Driven Development Pattern + Parallel Dispatch Pattern + Writing Skills Pattern

**Announce:** `## 🔧 [Stage 3 — CREATE] Using TDD + Subagent-Driven Development Patterns`

### Step 1: For Each Task — Follow TDD (strict)

**RED — Write Failing Test First:**
```
- Write ONE test per behavior
- Name clearly describes behavior
- Use real code (no mocks unless unavoidable)
- NO production code without a failing test first
```
**Verify RED — Watch It Fail:**
```
- Run the test
- Confirm it fails (for the RIGHT reason — feature missing, not typo)
- If it passes, you're testing existing behavior → FIX THE TEST
- If it errors, fix the error → re-run until it fails correctly
```
**GREEN — Minimal Implementation:**
```
- Write SIMPLEST code to pass the test
- No YAGNI features, no "while I'm here" improvements
- Don't add what the test doesn't require
```
**Verify GREEN — Watch It Pass:**
```
- Run the test
- Confirm it passes
- Other tests still pass
- Output pristine (no errors/warnings)
- If fails → FIX THE CODE, not the test
```
**REFACTOR — Clean Up (while staying green):**
```
- Remove duplication
- Improve names
- Extract helpers
- Keep tests green
- Don't add behavior
```

**IRON LAW:** `NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST.` Write code before test? Delete it. Start over. No exceptions.

### Step 2: Dispatch Per-Task Subagents

For independent tasks, spawn fresh sub-agents (NOT your session context):
```
Agent("Implement Task N: <description>")
```
Each sub-agent gets:
- Complete task text and context (don't make them read the plan file)
- TDD instructions embedded above
- Self-review before reporting done

### Step 3: Two-Stage Review Per Task

After each task sub-agent completes:
1. **Spec Review:** Does code match the plan? Nothing missing, nothing extra?
2. **Code Quality Review:** Is implementation clean and well-structured?

Both must pass before moving to next task.

### Step 4: Parallel Dispatch for Independent Tasks

If tasks have NO shared state or sequential dependencies, dispatch them in parallel — one agent per independent domain.

### Step 5: Create Missing Capabilities

If you discover a reusable pattern/capability is missing during creation:
```
Write a brief skill definition: what it is, when to use, core pattern.
Save as skill for future reference.
```
Do NOT improvise undocumented logic.

### Step 6: Council Head Check
- All components implemented and TDD-verified?
- All tests pass?
- All Critic concerns resolved?

If YES → `council-orchestrator advance create "all done"` → **GOTO LOOP step 1**
If NO → `council-orchestrator loopback create "<reason>"` → **GOTO LOOP step 1**

---

## Stage 4 — REVIEW & TEST

### Uses Embedded: Code Review Pattern + Systematic Debugging Pattern + Verification Pattern

**Announce:** `## 🔍 [Stage 4 — REVIEW & TEST] Using Code Review + Systematic Debugging Patterns`

### Step 1: Pre-Review Checklist
Before reviewing:
- Get git SHAs: `BASE_SHA=$(git rev-parse HEAD~1)` `HEAD_SHA=$(git rev-parse HEAD)`
- Brief summary: what was built and what it should do

### Step 2: Full Review
**Dispatching all council roles to review simultaneously:**
```
Agent("Reviewer — logic & correctness"):
  "Review for: logic errors, correctness bugs, edge cases, integration gaps"

Agent("Critic — security & performance"):
  "Review for: security gaps, performance issues, anti-patterns, maintainability"

Agent("Verifier — completeness"):
  "Review: does the output fully satisfy the original objective?"
```

### Step 3: Evaluate Feedback
When receiving review feedback:
1. **READ** — Complete feedback without reacting
2. **UNDERSTAND** — Restate requirement or ask for clarification
3. **VERIFY** — Check against codebase reality
4. **EVALUATE** — Technically sound for THIS codebase?
5. **RESPOND** — Technical acknowledgment or reasoned pushback
6. **IMPLEMENT** — One item at a time, test each

**Never:** performative agreement ("you're absolutely right!"), blind implementation, batch without testing.

**Push back if:** suggestion breaks existing functionality, reviewer lacks full context, violates YAGNI, technically incorrect for this stack.

### Step 4: Produce Review Report
Write `REVIEW_ISSUES.md` with all findings categorized:
- Critical — must fix now
- Important — fix before proceeding
- Minor — note for later

### Step 5: If Flaws Detected — Apply Systematic Debugging

**Phase 1 — Root Cause Investigation (BEFORE any fix):**
```
1. Read error messages carefully — stack traces, line numbers
2. Reproduce consistently — exact steps, every time?
3. Check recent changes — git diff, recent commits
4. Trace data flow — where does the bad value originate?
```
**Phase 2 — Pattern Analysis:**
```
1. Find working examples — similar code that works
2. Compare against references — read completely
3. Identify differences — what's different between working and broken?
```
**Phase 3 — Hypothesis and Testing:**
```
1. Form single hypothesis — "I think X is root cause because Y"
2. Test minimally — smallest possible change, one variable at a time
3. Verify before continuing — worked? Yes → fix. No → new hypothesis.
```
**Phase 4 — Implementation:**
```
1. Create failing test case — simplest possible reproduction
2. Implement single fix — ONE change, address root cause
3. Verify fix — test passes, no regressions
4. If 3+ fixes failed → STOP. Question the architecture.
```

**IRON LAW:** `NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST.`

### Step 6: Fix Loop
- Found flaw → apply Systematic Debugging → fix → re-verify
- `council-orchestrator loopback review "<reason>"` → re-run review → **GOTO LOOP step 1**
- Repeat until `REVIEW_ISSUES.md` has ZERO unresolved issues

### Step 7: Advance
`council-orchestrator advance review "all clear"` → **GOTO LOOP step 1**

---

## Stage 5 — VERIFY & DELIVER

### Uses Embedded: Verification Pattern + Finishing Branch Pattern

**Announce:** `## ✅ [Stage 5 — VERIFY & DELIVER] Using Verification + Branch Finishing Patterns`

### Step 1: Verification Gate
**IRON LAW:** `NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE.`

For EVERY claim, follow this gate:
```
1. IDENTIFY — What command proves this claim?
2. RUN — Execute the FULL command (fresh, complete)
3. READ — Full output, check exit code, count failures
4. VERIFY — Does output confirm the claim?
   - If NO: State actual status with evidence
   - If YES: State claim WITH evidence
```

**Red flags:** Using "should", "probably", "seems to" before verification. Expressing satisfaction before verifying. Trusting agent success reports without checking.

### Step 2: Full Integration Verification
```
- Run the FULL test suite — not just unit tests
- Build the project — confirm compilation
- Check all integration points
- Run any manual verification steps
- Output: full verification log
```

### Step 3: Completeness Check
```
Agent(description="Completeness verifier", prompt="""
Original objective: <objective>
Completion criteria: <from council_journal.md>

Verify EVERY criterion. Check:
- Is every requirement met?
- Is output complete and self-contained?
- Any edge cases or gaps?
- Can the output be used as-is?

Produce VERIFICATION_SIGN_OFF.md
- If ALL satisfied: "VERIFIED — Ready to deliver"
- If ANY unsatisfied: state each gap explicitly
""")
```

### Step 4: Branch Finishing (if code to merge)
```
1. Verify tests pass
2. Detect environment (normal repo vs worktree)
3. Determine base branch (main/master)
4. Present options (for user interaction if needed):
   - Merge locally
   - Push and create PR
   - Keep branch as-is
   - Discard
```

### Step 5: Decision
- Verified → `council-orchestrator advance verify "passed"` → **GOTO LOOP step 1**
- Not verified → `council-orchestrator loopback verify "<reason>"` → **GOTO LOOP step 1**

---

## Delivery Check

When `council-orchestrator status` shows `stage: __delivery_check__`:

**Step 1:** Read objective from `council_journal.md`
**Step 2:** Read output (all created files, VERIFICATION_SIGN_OFF.md)
**Step 3:** Compare output to completion criteria

**If objective FULLY satisfied:**
```
## 📦 [DELIVERY] Objective satisfied!
## 🎯 Objective: <objective>
## ✅ Iterations: N | Total loops: M
## 📄 Output: <path>
```
Present final output. **STOP THE LOOP.**

**If NOT fully satisfied:**
```
## 🔄 [LOOP] Iteration N complete — objective not fully satisfied
## 📋 Unsatisfied: <gaps>
## 🚀 Starting Iteration N+1 with accumulated context
```
```bash
council-orchestrator next-iteration
```
Then **GOTO LOOP step 1** — stage is now "think" again with ALL accumulated context.

---

## Context Management

When context window reaches **140,000 tokens**:
1. `council-orchestrator compact`
2. Run `/compact`
3. Re-read `council_journal.md`
4. `council-orchestrator status`
5. Continue from indicated stage

Never compact mid-sub-agent task — finish the atomic unit first.

---

## Standing Directives (The Constitution)

| # | Directive | Rule |
|---|---|---|
| 1 | **NEVER STOP** | No user input needed. Resolve blockers autonomously. Never ask "should I continue?" |
| 2 | **GOTO LOOP step 1** | After every stage action, IMMEDIATELY go back to status check |
| 3 | **TDD always** | NO production code without a failing test first. Write code first? Delete it. |
| 4 | **Verify before claiming** | NO "it works" without fresh command output. Run the command, read the output. |
| 5 | **Root cause before fix** | NO fix without investigation first. Symptom fixes are failure. |
| 6 | **Never silence Critic** | Critic must report at Stages 1, 2, 3. Explicit "no concerns" if none. |
| 7 | **Never bundle tasks** | Each atomic task gets its own sub-agent. One behavior per test. |
| 8 | **Never lose context** | Journal is truth. Full history carried through every stage. |
| 9 | **Never deliver unverified** | Only after Stage 5 sign-off AND delivery check pass. |
| 10 | **Dual-test Stage 3** | Run spec review THEN code quality review. Both must pass. |
| 11 | **Create missing capabilities** | Don't improvise. Write the pattern as a skill. |
| 12 | **Auto-compact at 140K** | Run /compact when context ≥ 140K. Never wait until overflow. |
| 13 | **Safety limit: 50 iterations** | Journal preserved if hit. Manual intervention needed. |
| 14 | **Deadman switch** | 10+ loops on same stage? Radically change approach. |

---

## Embedded Skills — Quick Reference

This file IS the complete superpower library. All 14 patterns are embedded above in their respective stages. Cross-reference:

| Look For | Stage | Pattern Name | IRON LAW |
|---|---|---|---|
| Exploring ideas, comparing architectures | 1 — THINK | Brainstorming | No implementation without design approval |
| Breaking down work into tasks | 2 — PLAN | Writing Plans | No TBD/TODO/placeholders. Every step has real code. |
| Isolating work | 2 — PLAN | Git Worktrees | Work in isolation. No worktree on main branch. |
| Running independent tasks concurrently | 3 — CREATE | Parallel Dispatch | Independent domains only. No shared state. |
| Task-by-task execution | 3 — CREATE | Subagent-Driven Dev | Fresh subagent per task. Two-stage review after each. |
| Writing code that works | 3 — CREATE | TDD | NO production code without a failing test first. |
| Missing capability during build | 3 — CREATE | Writing Skills | Write the pattern. Don't improvise. |
| Reviewing code quality | 4 — REVIEW | Code Review | Pre-review checklist before ANY review begins. |
| Pre-review checklist | 4 — REVIEW | Requesting Review | Get git SHAs. Dispatch reviewer. Act on feedback. |
| Responding to feedback | 4 — REVIEW | Receiving Review | Verify before implementing. Push back if wrong. |
| Fixing bugs | 4 — REVIEW | Systematic Debugging | No fixes without root cause investigation first. |
| Confirming fixes | 4 — REVIEW & 5 | Verification Before Completion | No claims without fresh command output. |
| Merging, PR, finishing | 5 — VERIFY | Finishing Branch | Verify tests first. Then present options. |
| **Model discovery** | **Step 0** | **Live Model Catalog** | **Run `council-orchestrator models` before starting** |

---

## Activation

1. **Model discovery:** `council-orchestrator models`
2. **Announce:** `## 🔵 [Init] Council starting — all 14 patterns embedded inline, zero external dependencies`
3. **Initialize:** `council-orchestrator init "<full objective>"`
4. **ENTER MAIN LOOP** — `council-orchestrator status`

**The council is active. All patterns are built in. The loop is turning.**
