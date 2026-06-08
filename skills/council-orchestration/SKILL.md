---
name: council-orchestration
description: Autonomous autoresearch-style loop through Think→Plan→Create→Review→Verify — iterates until objective is fully satisfied. Invokes superpowers skills at every stage. Never stops until query is resolved.
---

# Council Orchestration — Autonomous Loop

## Overview

A **self-looping, never-stopping** multi-agent pipeline that cycles through 5 stages (Think → Plan → Create → Review → Verify) until the original query is fully resolved.

**Inspired by Karpathy's autoresearch:** each iteration is self-contained; the loop runs autonomously without user intervention. If the output doesn't satisfy the objective, the council loops back to Stage 1 with all accumulated context and trys again.

**Core principle:** NEVER STOP. No "should I continue?" questions. No pausing for approval. Each stage invokes the appropriate **superpowers skills** explicitly via the Skill tool — not just references them. The loop keeps turning until the objective is met or the safety limit is hit.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   MAIN ORCHESTRATION LOOP                        │
│                                                                  │
│  while not objective_fully_satisfied:                            │
│    ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐        │
│    │THINK │→  │PLAN  │→  │CREATE│→  │REVIEW│→  │VERIFY│        │
│    │  +   │   │  +   │   │  +   │   │  &   │   │  &   │        │
│    │CRITIC│   │CRITIC│   │CRITIC│   │ TEST │   │DELIVER│        │
│    └──┬───┘   └──┬───┘   └──┬───┘   └──┬───┘   └──┬───┘        │
│       │           │          │          │          │             │
│       ◄───────────┴──────────┴──────────┴──────────┤             │
│       │  loop back if critiqued or issues found     │             │
│       └─────────────────────────────────────────────┘             │
│                    │  if verify passes but objective unmet         │
│                    └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## State Management

The council maintains a **`council_journal.md`** file in the working directory. This is the persistent state — read at each wakeup, written after every stage transition.

**Initialize with:**
```bash
python orchestrator.py init "<your_objective>"
```

**Track progress with:**
```bash
python orchestrator.py status        # Current stage, iteration, loops
python orchestrator.py advance think  # Mark stage done, advance
python orchestrator.py loopback think "Reason why"  # Go back to fix
python orchestrator.py next-iteration # Start fresh iteration
python orchestrator.py history        # Full state history
```

## Superpowers Integration

Every stage **EXPLICITLY invokes** superpowers skills via the `Skill` tool. Do not merely describe what a skill does — invoke it.

| Stage | Skill Invocations |
|---|---|
| **Init** | `Skill(skill="using-superpowers")` |
| **1 — Think** | `Skill(skill="superpowers:brainstorming")`, then spawn Thinker + Critic sub-agents |
| **2 — Plan** | `Skill(skill="superpowers:writing-plans")`, spawn Planner + Critic |
| **3 — Create** | `Skill(skill="superpowers:dispatching-parallel-agents")`, `Skill(skill="superpowers:subagent-driven-development")`, `Skill(skill="superpowers:test-driven-development")`, `Skill(skill="superpowers:writing-skills")` |
| **4 — Review & Test** | `Skill(skill="superpowers:code-review")`, `Skill(skill="superpowers:systematic-debugging")`, `Skill(skill="superpowers:verification-before-completion")` |
| **5 — Verify & Deliver** | `Skill(skill="superpowers:verification-before-completion")`, `Skill(skill="superpowers:finishing-a-development-branch")` |

---

## The Main Loop

### Activation Protocol

On receiving any objective:

1. **Announce:** `## 🔵 [Init] Invoking: \`using-superpowers\` | Loading skills system`
2. **Execute:** `Skill(skill="using-superpowers")` — loads and validates all superpowers
3. **Initialize state:**
   ```bash
   python orchestrator.py init "<the user's full objective>"
   ```
4. **Read state:**
   ```bash
   python orchestrator.py status
   ```
5. **Enter the main loop** — see below

### The NEVER-STOP Loop

```
python orchestrator.py status   ← check where we are
                                   
if stage == "think"             → execute Stage 1
if stage == "plan"              → execute Stage 2
if stage == "create"            → execute Stage 3
if stage == "review"            → execute Stage 4
if stage == "verify"            → execute Stage 5
if stage == "__delivery_check__" → check satisfaction → deliver or loop
if stage == "__maxed_out__"     → output summary, journal preserved
```

After each stage, call:
```bash
python orchestrator.py status
```
to see what the orchestrator says next. Follow its direction.

**NEVER ask the user "should I continue?" or "is this good?"** The loop is autonomous. The answer is always "continue" until the objective is met.

---

## Stage 1 — THINK

### Invoke: `brainstorming` + Spawn Thinker sub-agent + Spawn Critic sub-agent

**Step 1 — Announce:**
```
## 💭 [Stage 1 — THINK] Invoking: brainstorming | Agent: Thinker
```

**Step 2 — Invoke brainstorming skill:**
```
Skill(skill="superpowers:brainstorming", args="<the objective>")
```
Let the brainstorming skill load. Follow its Socratic refinement process.

**Step 3 — Spawn Thinker sub-agent:**
```
Agent(description="Thinker deep analysis", prompt="""
You are the Thinker in an AI Council. Your job:
1. Read the objective: <objective>
2. Analyze every interpretation, constraint, dependency, edge case
3. Compare multiple solution architectures (at least 3)
4. Select the strongest approach via Socratic refinement
5. Produce a Thought Report with:
   - All interpretations considered
   - Constraints and dependencies mapped
   - Risk analysis
   - 3+ architectures compared (pros/cons per architecture)
   - Recommended approach with justification
6. Save to THOUGHT_REPORT.md
""", subagent_type="general-purpose")
```

**Step 4 — Spawn Critic sub-agent in parallel:**
```
Agent(description="Critic challenge thought report", prompt="""
You are the Critic in an AI Council. Read the Thought Report being produced.
Your adversarial mandate — assume the current approach is wrong:
- What assumptions in the Thought Report could be false?
- What risks or edge cases were not considered?
- Is the selected architecture actually the strongest?
- What pros/cons were missed or downplayed?
- What could go wrong?

Produce CRITIQUE_REPORT.md with explicit concerns.
If no concerns, state: "No concerns — approach is sound."
""", subagent_type="general-purpose")
```

**Step 5 — Council Head reviews both reports.**
- If Critic has concerns → `python orchestrator.py loopback think "<reason>"` → recall Thinker
- If no concerns → `python orchestrator.py advance think "thought report + critique approved"`

---

## Stage 2 — PLAN

### Invoke: `writing-plans` + Spawn Planner sub-agent + Spawn Critic sub-agent

**Prerequisite:** Stage 1 must be complete. Read THOUGHT_REPORT.md and CRITIQUE_REPORT.md.

**Step 1 — Announce:**
```
## 📋 [Stage 2 — PLAN] Invoking: writing-plans | Agent: Planner
```

**Step 2 — Invoke writing-plans skill:**
```
Skill(skill="superpowers:writing-plans", args="Plan implementation for: <objective>")
```

**Step 3 — Spawn Planner sub-agent:**
```
Agent(description="Planner task decomposition", prompt="""
You are the Planner in an AI Council.
Input: THOUGHT_REPORT.md (the selected architecture)
Invoke: writing-plans skill (just loaded)
Produce a TASK_EXECUTION_PLAN.md with:
- Discrete, ordered, atomic tasks with success criteria
- Parallel vs. sequential dependencies flagged
- Each task assigned to appropriate sub-agent
- Git worktrees configured for parallel branches
- Batch checkpoints defined
- For each task: expected output, effort estimate, risk level
""", subagent_type="general-purpose")
```

**Step 4 — Spawn Critic sub-agent in parallel:**
```
Agent(description="Critic challenge plan", prompt="""
You are the Critic. Read the Task Execution Plan being produced.
- Are any tasks under-specified or missing success criteria?
- Are dependencies correctly identified?
- Does the plan cover all risks from Stage 1?
- What could cause the plan to fail or go over scope?
- Are the effort estimates realistic?
- Is there a simpler sequencing approach?

Produce PLAN_CRITIQUE.md.
""", subagent_type="general-purpose")
```

**Step 5 — Council Head reviews.**
- If Critic has concerns → `python orchestrator.py loopback plan "<reason>"` → recall Planner
- If no concerns → `python orchestrator.py advance plan "plan approved"`

---

## Stage 3 — CREATE

### Invoke: `dispatching-parallel-agents` + `subagent-driven-development` + `test-driven-development` + `writing-skills`

**Prerequisite:** Read TASK_EXECUTION_PLAN.md and PLAN_CRITIQUE.md.

**Step 1 — Announce:**
```
## 🔧 [Stage 3 — CREATE] Dispatching parallel creators | Using TDD
```

**Step 2 — Invoke parallel dispatch skill:**
```
Skill(skill="superpowers:dispatching-parallel-agents", args="Run independent Create tasks concurrently")
```

**Step 3 — For EACH task in the plan, invoke subagent-driven-development:**
```
Skill(skill="superpowers:subagent-driven-development", args="<task description>")
```
This spawns a fresh sub-agent per task with mandatory two-stage review.

**Step 4 — Enforce TDD on every component:**
```
Skill(skill="superpowers:test-driven-development", args="<component>")
```
RED → GREEN → REFACTOR cycle on every component. NO component passes without:
- Test written first (RED)
- Implementation makes it pass (GREEN)
- Code is refactored for clarity (REFACTOR)

**Step 5 — Spawn Critic sub-agent per component:**
```
Agent(description="Critic review component", prompt="""
Review the just-completed component:
- Does it match the plan's intent, or has it drifted?
- What could go wrong at runtime / under load / at integration?
- Is there a simpler or more robust approach?
- Any security, performance, or maintainability concerns?
- Pros and cons of the implementation approach chosen
""", subagent_type="general-purpose")
```

**Step 6 — Dual-Test Protocol:** After Critic sign-off on a component:
- Run `subagent-driven-development` AND `verification-before-completion` in parallel
- First to pass full verification is canonical; the other is discarded

```
Skill(skill="superpowers:verification-before-completion", args="<component>")
```

**Step 7 — Create missing reusable capabilities:**
```
Skill(skill="superpowers:writing-skills", args="Create skill for: <missing capability>")
```

**Step 8 — Council Head checks:**
- All components implemented and tested?
- All Critic concerns resolved?
- All tests pass (TDD confirmed)?

If YES → `python orchestrator.py advance create "all components implemented and tested"`
If NO → `python orchestrator.py loopback create "<reason>"` → fix and retry

---

## Stage 4 — REVIEW & TEST

### Invoke: `code-review` + `systematic-debugging` + `verification-before-completion`

**Step 1 — Announce:**
```
## 🔍 [Stage 4 — REVIEW & TEST] Running full council review
```

**Step 2 — Invoke code-review skill:**
```
Skill(skill="superpowers:code-review", args="Review all created code for correctness and cleanups")
```
Use the code-review skill's pre-review checklist first, then full review.

**Step 3 — Spawn ALL council roles to review simultaneously:**
```
Agent(description="Reviewer logic & correctness", prompt="Review for logic errors, correctness bugs, edge cases")
Agent(description="Critic security & performance", prompt="Review for security gaps, performance issues, anti-patterns")
Agent(description="Verifier completeness", prompt="Review: does output fully satisfy the original objective?")
```

**Step 4 — Invoke receiving-code-review if feedback received:**
```
Skill(skill="superpowers:receiving-code-review", args="Review feedback received: <summary>")
```
No feedback dismissed without documented reasoning.

**Step 5 — Re-enforce TDD — retest all components post-review:**
```
Skill(skill="superpowers:test-driven-development", args="Re-test all components after review")
```

**Step 6 — Produce REVIEW_ISSUES.md with all findings.**

**If ANY flaw detected:**

1. Announce: `## ❌ [Stage 4] Issue detected | Reason: <issue>`
2. Invoke systematic-debugging:
   ```
   Skill(skill="superpowers:systematic-debugging", args="<issue>")
   ```
3. Follow the 4-phase root cause diagnosis:
   - **Phase 1:** Observe — gather symptoms
   - **Phase 2:** Hypothesize — possible root causes
   - **Phase 3:** Experiment — test each hypothesis
   - **Phase 4:** Fix — apply targeted fix, don't touch working code
4. Once fixed, invoke verification:
   ```
   Skill(skill="superpowers:verification-before-completion", args="Confirm fix works")
   ```
5. `python orchestrator.py loopback review "<reason>"` → re-run review
6. Repeat until REVIEW_ISSUES.md has zero unresolved issues

**Step 7 — When clean:** `python orchestrator.py advance review "all issues resolved, tests pass"`

---

## Stage 5 — VERIFY & DELIVER

### Invoke: `verification-before-completion` + `finishing-a-development-branch`

**Step 1 — Announce:**
```
## ✅ [Stage 5 — VERIFY & DELIVER] Running final verification
```

**Step 2 — Invoke verification-before-completion:**
```
Skill(skill="superpowers:verification-before-completion", args="End-to-end verification of complete solution")
```
Confirm every component is functional as an integrated whole.

**Step 3 — Full satisfaction check:**
```
Agent(description="Completeness verifier", prompt="""
Original objective: <objective>
Completion criteria: <from council_journal.md>

Verify EVERY criterion is satisfied. Check:
- Is every requirement from the objective met?
- Is the output complete and self-contained?
- Are there any edge cases or gaps?
- Can the output be used as-is?

Produce VERIFICATION_SIGN_OFF.md
- If ALL satisfied: state "VERIFIED — Ready to deliver"
- If ANY unsatisfied: state each gap explicitly
""", subagent_type="general-purpose")
```

**Step 4 — If code/output needs to be merged:**
```
Skill(skill="superpowers:finishing-a-development-branch", args="Merge and finalize")
```


**Step 5 — Decision:**
- If verified → `python orchestrator.py advance verify "verification passed"` → move to delivery check
- If not verified → `python orchestrator.py loopback verify "<reason>"` → fix, re-verify

---

## Delivery Check (after Stage 5 passes)

**The critical gate:** does the output FULLY satisfy the original objective?

```bash
python orchestrator.py status
```

If stage is `__delivery_check__`:

1. **Compare output to original objective** — read the objective, read the output
2. `python orchestrator.py check <output_path>` — formal completion check
3. **If output fully satisfies objective:**
   ```
   ## 📦 [DELIVERY] Objective satisfied | Iteration: N | Total loops: M
   ## 🎯 Objective: <objective>
   ## ✅ Criteria met:
   ##    - <all satisfied criteria>
   ## 📄 Output: <path to output>
   ```
   Present the final output to the user. Done.

4. **If output does NOT fully satisfy the objective:**
   ```
   ## 🔄 [LOOP] Iteration N complete but objective not fully satisfied
   ## 📋 Unsatisfied: <gaps>
   ## 🚀 Starting Iteration N+1 with accumulated context + learnings
   ```
   ```bash
   python orchestrator.py next-iteration
   ```
   Then go back to **Stage 1 — THINK**, starting a new iteration with ALL accumulated context and learnings from previous iterations.

---

## Context Management Protocol

**Context overflow silently corrupts long pipeline runs. Monitor token usage continuously.**

### Auto-Compaction Rule

When the active window reaches **140,000 tokens**, run compaction:

1. Compact the journal: `python orchestrator.py compact`
2. Run `/compact` in the Claude Code session
3. After compacting, continue from the last checkpoint:
   - Re-read `council_journal.md`
   - Run `python orchestrator.py status`
   - Continue from the stage indicated

### Never compact mid-stage
If a sub-agent is actively working, let it finish the current atomic unit first, then compact.

---

## Standing Directives (The Constitution)

| # | Directive | Rule |
|---|---|---|
| 1 | **NEVER STOP** | No stage waits for user input; blockers resolved autonomously. Never ask "should I continue?" |
| 2 | **Always check state** | Before any action, run `python orchestrator.py status` — know where you are |
| 3 | **Never skip review** | Every stage output reviewed by Council Head before advancing |
| 4 | **Never silence the Critic** | Critic produces a report at Stages 1, 2, 3 — explicit "no concerns" if none |
| 5 | **Never bundle tasks** | Each atomic task gets its own sub-agent |
| 6 | **Never lose context** | Full history, decisions, and invocations carried through every stage. Journal is truth |
| 7 | **Never deliver unverified** | Final output released only after Stage 5 sign-off AND delivery check |
| 8 | **Preserve what works** | During debugging, only broken components are touched |
| 9 | **Dual-test Stage 3** | Both implementations tested in parallel; first to pass is canonical |
| 10 | **Create skills when needed** | Missing capability → `Skill(skill="superpowers:writing-skills")`, never improvise |
| 11 | **Auto-compact at 140K** | Run `/compact` when context ≥ 140K tokens — never wait until overflow |
| 12 | **Safety limit: 50 iterations** | If max_iterations reached, output summary and journal — manual intervention needed |
| 13 | **Deadman switch** | If no progress for 30 minutes across the same stage, escalate: try radically different approach |

---

## Announcement Protocol

**Every agent MUST print announcements before and after every skill invocation, sub-agent dispatch, and model call. Silence is forbidden.**

| Action | Format |
|---|---|
| Entering a stage | `## 🔵 [Stage N — NAME] Invoking: \`skill-name\` | Agent: Role` |
| Stage complete | `## ✅ [Stage N — NAME] Complete | → Next: Stage N+1` |
| Critic starts | `## 🔍 [Stage N — Critic] Reviewing in parallel` |
| Critic done | `## ✅ [Stage N — Critic] Report ready | Concerns: <count or "none">` |
| Sub-agent dispatched | `## 🚀 [Stage N] Sub-agent: Role | Task: <brief>` |
| Error / recall | `## ❌ [Stage N] Issue | Recall: Agent | Reason: <brief>` |
| Loop back | `## 🔄 [Stage N] Looping back to Stage M | Reason: <brief>` |
| New iteration | `## 🔄 [NEW ITERATION] Iteration N+1 starting | Stage: think` |
| Delivery | `## 📦 [DELIVERY] Objective satisfied! | Iterations: N | Loops: M` |

---

## Activation

On receiving any objective:

1. **Announce:** `## 🔵 [Init] Invoking: \`using-superpowers\` | Loading skills system`
2. **Execute:** `Skill(skill="using-superpowers")` — loads the skills system
3. **Initialize:** `python orchestrator.py init "<objective>"`
4. **Enter main loop:**
   - `python orchestrator.py status` → find current stage
   - Execute that stage with full superpowers integration
   - Advance or loopback based on results
   - NEVER STOP until objective is met or safety limit hit
5. **Deliver:** When __delivery_check__ says objective met, present final output

**The council is active. The loop is turning. Awaiting the objective — or already executing.**
