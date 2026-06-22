---
name: council-orchestration
description: Fully self-contained autonomous autoresearch loop with dynamic domain-aware agent teams — Boot→Think→Plan→Create→Review→Verify. Scans project, auto-generates expert team personas (Head + Thinking Team + Execution Team + Critic + Testing Agent) tailored to any domain. Teams debate internally before reporting to Head. ALL superpower skills embedded inline, zero external dependencies.
---

# Council Orchestration — Domain-Aware Multi-Agent Loop

**Everything is built-in.** All 14 superpower patterns are embedded directly in this file. No external Skill calls needed. The council reads, applies, and loops autonomously until the objective is met.

**New in this version:** Phase 0 PROJECT BOOT — scans the project, infers domain, generates domain-appropriate expert agent personas, and assembles a project-specific team before any work begins.

**Model reference:** All available models via proxy can be discovered live with `council-orchestrator models`.

---

## Architecture

```
PHASE 0 — PROJECT BOOT (runs once at session start):
  Scan project → Infer domain → Generate COUNCIL_AGENTS.md
  ↓
MAIN LOOP (autonomous, never stop):

LOOP:
  1. council-orchestrator status          ← check current stage
  2. Execute the stage handler            ← uses embedded patterns below
  3. council-orchestrator status          ← verify transition
  4. GOTO step 1                          ← UNCONDITIONAL

BREAK ONLY when:
  - Delivery check says objective satisfied → DELIVER
  - __maxed_out__ safety limit → REPORT

  ┌────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌──────────┐  ┌──────────┐
  │  BOOT  │→ │  THINK  │→ │  PLAN   │→ │ CREATE  │→ │  REVIEW  │→ │  VERIFY  │
  │ (once) │  │ Thinking│  │Thinking+│  │Execution│  │Critic+   │  │ Testing  │
  │        │  │  Team   │  │Execution│  │  Team   │  │ Testing  │  │  Agent   │
  └────────┘  └────┬────┘  └────┬────┘  └────┬────┘  └────┬─────┘  └────┬─────┘
                   │             │             │             │              │
                   ◄─────────────┴─────────────┴─────────────┴──────────────┘
                   │   loop back via loopback if teams find issues             │
                   └───────────────────────────────────────────────────────────┘
                         │  if !satisfied → next-iteration → GOTO top
                         └──────────────────────────────────────────┘
```

### Agent Hierarchy

```
                    ┌──────────────────┐
                    │   HEAD AGENT     │  ← Orchestrator. Domain's lead coordinator.
                    │  (1 agent)       │    Receives reports, routes tasks, approves/rejects.
                    └────────┬─────────┘
           ┌─────────────────┼──────────────────┬──────────────────┐
           ▼                 ▼                  ▼                  ▼
  ┌─────────────────┐  ┌───────────────┐  ┌──────────────┐  ┌────────────────┐
  │  THINKING TEAM  │  │EXECUTION TEAM │  │ CRITIC AGENT │  │ TESTING AGENT  │
  │  (2+ agents)    │  │  (2+ agents)  │  │  (1 agent)   │  │   (1 agent)    │
  │                 │  │               │  │              │  │                │
  │ Domain thinkers │  │Domain builders│  │Domain external│ │Domain verifier │
  │ & strategists   │  │& implementors │  │  challenger   │ │& quality gate  │
  └─────────────────┘  └───────────────┘  └──────────────┘  └────────────────┘
```

**All titles are DYNAMIC** — generated at boot based on the project's detected domain. A cooking app gets chefs and food inspectors. A legal firm gets lawyers and senior partners. A medical system gets doctors and clinical validators.

---

## State Management

```bash
council-orchestrator init "<objective>"          # Start (stage begins at "boot")
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
- Head/Thinker/Critic → claude-opus-4.6-1m (strongest)
- Planner/Reviewer → claude-sonnet-4.6 (balanced)
- Creator/Executor → gpt-5.4 or gpt-5.2
- Testing/Verifier → claude-haiku-4.5 (cheapest) or gpt-5-mini (FREE)

**If only OpenCode Zen:**
- Head/Thinker/Critic → deepseek-v4-pro, qwen3.7-max, kimi-k2.6
- Planner/Reviewer → qwen3.6-plus, minimax-m2.7
- Creator/Executor → deepseek-v4-flash, minimax-m2.7
- Testing/Verifier → deepseek-v4-flash-free (FREE) or any free model

**For multi-model orchestration,** use the sibling skill `ai-council-orchestration` which switches models per-stage.

---

## The Main Loop

```
LOOP:
  1. Run: council-orchestrator status
  2. Match the "Stage:" field:
     "boot"              → execute Phase 0 — PROJECT BOOT (once, at session start)
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

## Phase 0 — PROJECT BOOT

### Dynamic Domain-Aware Agent Generation

**Announce:** `## 🚀 [Phase 0 — BOOT] Scanning project and assembling domain-aware agent team`

**This phase runs ONCE at session start. It generates the expert team that powers all subsequent stages.**

### Step 1: Project Scan

Read these files (in order of priority):
```
README.md, README.txt, README.rst
package.json, requirements.txt, setup.py, Cargo.toml, go.mod, pom.xml
.env.example (for clues, not secrets)
docs/, CONTRIBUTING.md, ARCHITECTURE.md
First 5 source files in the primary language
```

Collect:
- Project name
- Technology stack / language / frameworks
- What the project DOES (its purpose)
- Industry/domain signals (keywords, imports, domain terminology)

### Step 2: Domain Inference

Based on the scan, classify the domain. Examples (not exhaustive — any domain is valid):

| Domain Signals | Detected Domain |
|---|---|
| `lodash`, `react`, `django`, `api`, `webpack`, `jest` | Software / Web Development |
| `aml`, `kyc`, `sanctions`, `transaction monitoring`, `compliance` | AML / Financial Crime Compliance |
| `ledger`, `balance sheet`, `audit trail`, `GAAP`, `IFRS`, `CA` | Accounting / Audit |
| `plaintiff`, `defendant`, `statute`, `jurisdiction`, `legal brief` | Legal / Law |
| `patient`, `clinical`, `HIPAA`, `diagnosis`, `EHR`, `medical` | Healthcare / Medical |
| `recipe`, `ingredient`, `menu`, `chef`, `kitchen`, `cooking` | Food & Hospitality |
| `curriculum`, `student`, `lesson`, `pedagogy`, `LMS`, `course` | Education / EdTech |
| `portfolio`, `derivative`, `yield`, `P&L`, `trading`, `quant` | Finance / Trading |
| `property`, `tenant`, `lease`, `mortgage`, `escrow`, `realtor` | Real Estate |
| `logistics`, `shipment`, `warehouse`, `SKU`, `inventory`, `SCM` | Supply Chain / Logistics |

**If domain is unclear after scan → ask the user once:**
> "I scanned the project but the domain isn't clear. What industry or field does this project serve? (e.g., software, legal, audit, healthcare, education...)"

### Step 3: Generate Agent Personas

For the detected domain, generate domain-appropriate titles for each of the 6 agent roles. The titles must reflect REAL professionals who would work in that domain:

**Template for each agent:**
```markdown
## <Role Name>

**Title:** <Real-world professional title in this domain>
**Persona:** You are the <title> for the <project name> project. Your domain expertise is <domain>. Your specific mandate within the council is <mandate>. When evaluating work, you think like a <title> would: <domain-specific perspective>.
**Mandate:** <Specific job in the council>
**Domain perspective:** <How this domain expert evaluates quality>
```

**The 6 mandatory roles (all must be generated):**

1. **Head Agent** — The lead coordinator. Oversees all agents, routes tasks, accepts/rejects team outputs, makes final calls. Example titles: Chief Technology Officer, Chief Compliance Officer, Managing Partner, Medical Director, Head Chef, Chief Auditor.

2. **Thinker A** — Domain strategist. Thinks long-term, sees big picture, proposes architectural/strategic approaches. Example: Senior Architect, Financial Crime Analyst, Senior Counsel, Diagnostic Specialist.

3. **Thinker B** — Domain analyst. Investigates specifics, identifies risks and edge cases, challenges assumptions. Example: Risk Intelligence Analyst, Systems Researcher, Legal Researcher, Clinical Analyst.

4. **Executor A** — Domain implementor. Builds/creates/executes the primary deliverable. Example: Senior Developer, AML System Specialist, Associate Attorney, Medical Practitioner.

5. **Executor B** — Domain support implementor. Assists execution, handles secondary deliverables, documentation. Example: Software Engineer, Compliance Documentation Specialist, Paralegal, Research Nurse.

6. **Critic Agent** — External domain challenger. Acts as an outside auditor or skeptical expert. Assumes work is wrong until proven right. Example: Government Compliance Officer, Senior Code Reviewer, External Audit Partner, Peer Reviewer.

7. **Testing Agent** — Domain quality verifier. Runs all tests, validates all outputs, finds what doesn't work. Reports directly to Head. Example: QA Engineer, Regulatory Test Lead, Evidence Verifier, Clinical Validator.

### Step 4: Write COUNCIL_AGENTS.md

```markdown
# Council Agents

## Project: <project name>
## Domain: <detected domain>
## Generated: <timestamp>

---

## Head Agent
**Title:** <title>
**Persona:** <full persona description>
**Mandate:** Observe all teams. Route tasks. Accept or reject team consensus. Make final calls on loopbacks.

---

## Thinking Team

### Thinker A
**Title:** <title>
**Persona:** <full persona description>
**Mandate:** Propose strategic approaches during THINK and PLAN stages.

### Thinker B
**Title:** <title>
**Persona:** <full persona description>
**Mandate:** Investigate specifics, identify risks, challenge Thinker A's proposals.

---

## Execution Team

### Executor A
**Title:** <title>
**Persona:** <full persona description>
**Mandate:** Primary implementor during CREATE stage.

### Executor B
**Title:** <title>
**Persona:** <full persona description>
**Mandate:** Support implementation, handle documentation, secondary deliverables.

---

## Critic Agent
**Title:** <title>
**Persona:** <full persona description>
**Mandate:** Adversarial review. Assume approach is wrong. Challenge at Stages 1, 2, 3, 4.

---

## Testing Agent
**Title:** <title>
**Persona:** <full persona description>
**Mandate:** Run ALL tests. Find ALL errors. Report to Head. Never suppress failures.
```

### Step 5: Confirm and Advance

Display generated agent team to user:
```
🎯 Project: <name> | Domain: <domain>
👑 Head: <title>
🧠 Thinking Team: <Thinker A title> + <Thinker B title>
⚒️  Execution Team: <Executor A title> + <Executor B title>
🔍 Critic: <title>
🧪 Testing Agent: <title>
```

Then: `council-orchestrator advance boot "agent team assembled"` → **GOTO LOOP step 1**

**IRON LAW:** Every agent spawned in Stages 1–5 MUST have their persona from COUNCIL_AGENTS.md injected into their prompt. Generic "Thinker" prompts are forbidden after boot.

---

## Team Debate Protocol

**Used whenever a team (Thinking Team or Execution Team) must solve a problem together.**

### The 3-Round Debate

```
ROUND 1 — Independent Proposals:
  Agent A: "Here is my proposed approach: <approach>"
  Agent B: "Here is my proposed approach: <approach>"
  (each independent, no reading the other's yet)

ROUND 2 — Cross-Critique:
  Agent A reads B's proposal → "Here is what's wrong with B's approach: <critique>"
  Agent B reads A's proposal → "Here is what's wrong with A's approach: <critique>"
  (each critiques the other's flaws, risks, gaps)

ROUND 3 — Convergence:
  Agent A: "Given B's critique of mine and my critique of B, here is my revised position: <revised>"
  Agent B: "Given A's critique of mine and my critique of A, here is my revised position: <revised>"
  → If they agree → consensus reached
  → If still diverging → Head Agent arbitrates: "The correct path is X because Y"
```

### Producing Consensus

Write `TEAM_CONSENSUS.md`:
```markdown
# Team Consensus — <stage> — <topic>

## Team: <Thinking Team / Execution Team>
## Agents: <Thinker A title> + <Thinker B title>

### Round 1 Proposals
**<Agent A>:** <proposal summary>
**<Agent B>:** <proposal summary>

### Round 2 Critiques
**<Agent A> on <Agent B>'s proposal:** <critique>
**<Agent B> on <Agent A>'s proposal:** <critique>

### Round 3 Convergence
**Final Consensus:** <agreed approach>
**Key decision:** <most important choice made>
**Rejected alternatives:** <what was ruled out and why>
```

### Head Agent Review of Consensus

Head reads TEAM_CONSENSUS.md:
- **Accepts:** Consensus is sound, no gaps → proceed
- **Rejects:** "The consensus missed X / assumed Y incorrectly" → trigger new debate round with Head's feedback injected

**Testing Agent errors ALWAYS trigger a new team debate cycle** with the error report as additional context.

---

## Stage 1 — THINK

### Uses: Thinking Team (debate) + Critic Agent + Head Agent

**Announce:** `## 💭 [Stage 1 — THINK] Thinking Team assembling — reading COUNCIL_AGENTS.md`

**Load COUNCIL_AGENTS.md first.** All agents must be instantiated with their domain personas.

### Step 1: Explore Context
Head Agent assigns the Thinking Team: "Read project files, docs, recent commits. Understand what exists. Prepare independent proposals."

### Step 2: Thinking Team Debate — Architectures
Invoke **Team Debate Protocol** with topic: "Propose the best architecture for: `<objective>`"

Each Thinker (using their domain persona) independently proposes 1-2 architectures. Then they critique each other. Then converge.

Cover in debate:
- Architecture & components (through domain lens, adhering to Ponytail rules: YAGNI, standard library/native features first, no speculative abstractions)
- Data flow & interfaces (simplest and shortest path possible)
- Error handling & edge cases  
- Testing strategy (as this domain would validate)

### Step 3: Head Socratic Refinement
Head Agent stress-tests the Thinking Team consensus:
- **What domain-specific assumptions are being made?** Could they be false?
- **What regulatory/operational constraints are non-negotiable?**
- **What could fail in production in this domain?**

### Step 4: Produce Thought Report
Write `THOUGHT_REPORT.md` with: interpretations from domain perspective, constraints, risk analysis, 3+ architectures compared (pros/cons), recommended approach with domain-specific justification.

### Step 5: Apply Critic Agent
**Spawn Critic Agent** (using their domain persona from COUNCIL_AGENTS.md):
> "You are the <Critic title>. Assume the Thinking Team's approach is wrong. What domain-specific assumptions could be false? What risks were missed? Is this the strongest approach from a <domain> perspective? Produce `CRITIQUE_REPORT.md`. If no concerns, state EXACTLY: 'No concerns — approach is sound.'"

### Step 6: Resolve or Advance
- Critic has concerns → `council-orchestrator loopback think "<reason>"` → new Thinking Team debate with Critic concerns injected → **GOTO LOOP step 1**
- No concerns → Head approves → `council-orchestrator advance think "approved"` → **GOTO LOOP step 1**

---

## Stage 2 — PLAN

### Uses: Thinking Team + Execution Team (validation) + Critic Agent + Head Agent

**Announce:** `## 📋 [Stage 2 — PLAN] Thinking Team planning, Execution Team validating`

**Load COUNCIL_AGENTS.md.** Use domain personas throughout.

### Step 1: Map File Structure
Thinking Team debates file/module structure. Each Thinker proposes a structure → debate → consensus on which files are created/modified. Each file = one clear responsibility. Follow Ponytail rules: map the absolute minimum file structure needed. Avoid speculative helper files, single-implementation interfaces, or config bloat.

### Step 2: Execution Team Plan Validation
After Thinking Team produces task list, invoke **Execution Team** (not Thinking Team) to review feasibility:
- Executor A: "Can this actually be built this way? Are tasks realistic? Does it use standard libraries and native features instead of installing new dependencies?"
- Executor B: "Is the documentation plan complete? Are secondary tasks covered?"

### Step 3: Decompose into Bite-Sized Tasks
Each task = one action (2-5 minutes):
```
Task 1: Write failing test
Task 2: Run to confirm failure
Task 3: Implement minimal code
Task 4: Run to confirm pass
Task 5: Commit
```

### Step 4: Write Plan
Write `TASK_EXECUTION_PLAN.md` with:
- **Goal:** One sentence
- **Architecture:** 2-3 sentences  
- **Domain context:** Why this approach fits this domain
- **Tech Stack:** Key technologies
- **Tasks:** Each with: files touched, exact file paths, code in steps, expected output, exact commands
- **Assigned to:** Executor A or Executor B (per their domain mandate)

### Step 5: Self-Review Plan
Check:
- ✅ Spec coverage — every requirement maps to a task
- ✅ No placeholders ("TBD", "TODO", "implement later")
- ✅ Type consistency — function signatures match across tasks
- ✅ Actual code in every step, not descriptions

### Step 6: Apply Critic Agent
Spawn Critic (domain persona): "Are any tasks under-specified? Dependencies correct? Risks from Stage 1 covered? Would a <Critic title> approve this plan?"

### Step 7: Resolve or Advance
- Concerns → `council-orchestrator loopback plan "<reason>"` → **GOTO LOOP step 1**
- Clear → Head approves → `council-orchestrator advance plan "approved"` → **GOTO LOOP step 1**

---

## Stage 3 — CREATE

### Uses: Execution Team (TDD) + Testing Agent (gate) + Head Agent (routing)

**Announce:** `## 🔧 [Stage 3 — CREATE] Execution Team building — Testing Agent standing by`

**Load COUNCIL_AGENTS.md.** Executors build. Testing Agent validates after each task batch.

### Step 1: Execution Team — TDD (strict)

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
- Write SIMPLEST code to pass the test, adhering strictly to Ponytail's ladder (YAGNI → stdlib → native → one-line → minimum code)
- No unrequested abstractions, boilerplate, or dependencies
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
- Mark deliberate simplifications and shortcuts with a `ponytail: <ceiling>, <upgrade path>` comment
```

**IRON LAW:** `NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST.` Write code before test? Delete it. Start over. No exceptions.

### Step 2: Dispatch Per-Task Subagents (with domain personas)

For independent tasks, spawn fresh sub-agents with their COUNCIL_AGENTS.md personas:
```
Agent(persona=<Executor A from COUNCIL_AGENTS.md>, prompt="""
You are the <Executor A title> for the <project name> project.
Implement Task N: <description>
<TDD instructions>
Self-review before reporting done.
""")
```
Each sub-agent gets:
- Their full domain persona injected
- Complete task text and context
- TDD instructions embedded above
- Self-review before reporting done

### Step 3: Two-Stage Review Per Task

After each task sub-agent completes:
1. **Spec Review:** Does code match the plan? Nothing missing, nothing extra?
2. **Domain Quality Review:** Would the <Executor title> be satisfied with this quality?

Both must pass before moving to next task.

### Step 4: Parallel Dispatch for Independent Tasks

If tasks have NO shared state or sequential dependencies, dispatch them in parallel:
- Executor A handles Task set A
- Executor B handles Task set B
- They work simultaneously, Head collects and reconciles

### Step 5: Testing Agent Checkpoint

After Execution Team completes a batch, invoke Testing Agent (domain persona):
```
Agent(persona=<Testing Agent from COUNCIL_AGENTS.md>, prompt="""
You are the <Testing Agent title>. Run ALL tests, ALL linters, ALL builds.
Report EVERY failure. Do not suppress or minimize.
Produce TEST_RESULTS.md.
""")
```

If Testing Agent finds errors → **Head Agent routes to Execution Team for Debate + Fix** → Testing Agent re-runs → repeat until clean.

### Step 6: Create Missing Capabilities

If you discover a reusable pattern/capability is missing during creation:
```
Write a brief skill definition: what it is, when to use, core pattern.
Save as skill for future reference.
```
Do NOT improvise undocumented logic.

### Step 7: Head Agent Council Check
- All components implemented and TDD-verified?
- Testing Agent reports zero failures?
- All Critic concerns resolved?

If YES → `council-orchestrator advance create "all done"` → **GOTO LOOP step 1**
If NO → `council-orchestrator loopback create "<reason>"` → **GOTO LOOP step 1**

---

## Stage 4 — REVIEW & TEST

### Uses: Critic Agent + Testing Agent + Head Agent + Execution Team (fixes)

**Announce:** `## 🔍 [Stage 4 — REVIEW & TEST] Critic + Testing Agent activated`

**Load COUNCIL_AGENTS.md.** Use domain personas for all agents.

### Step 1: Pre-Review Checklist
Before reviewing:
- Get git SHAs: `BASE_SHA=$(git rev-parse HEAD~1)` `HEAD_SHA=$(git rev-parse HEAD)`
- Brief summary: what was built and what it should do
- Head Agent assigns review roles from COUNCIL_AGENTS.md

### Step 2: Full Review — Domain-Aware Parallel Review
**Dispatch simultaneously (use their COUNCIL_AGENTS.md personas):**
```
Agent(persona=<Critic from COUNCIL_AGENTS.md>):
  "As the <Critic title>: Review for logic errors, domain-specific correctness,
   edge cases, security gaps, anti-patterns, maintainability.
   Also run a ponytail-review for over-engineering and complexity. Find what to delete/simplify using tags:
   delete (dead code/flexibility), stdlib (reinvented stdlib), native (dependency doing what platform does),
   yagni (abstraction with 1 implementation), shrink (same logic, fewer lines).
   List location, what to cut, and what replaces it. Report the net lines removable.
   Would a <Critic title> approve this in production?"

Agent(persona=<Testing Agent from COUNCIL_AGENTS.md>):
  "As the <Testing Agent title>: Run ALL tests. Run linters. Run builds.
   Run every validation command. Report EVERY failure — do not suppress any.
   Produce TEST_RESULTS.md with full output."
```

### Step 3: Testing Agent Error Routing
When Testing Agent reports errors:
1. Head Agent reads TEST_RESULTS.md
2. Head routes to **Execution Team** with error context: "Fix these errors: <error list>"
3. Execution Team invokes **Team Debate Protocol** on the error: root cause → fix approach → consensus
4. Executors implement the fix (TDD: write failing test reproduction → fix → verify)
5. Testing Agent re-runs after fix
6. Repeat until TEST_RESULTS.md shows zero failures

### Step 4: Evaluate Feedback
When receiving Critic feedback:
1. **READ** — Complete feedback without reacting
2. **UNDERSTAND** — Restate requirement or ask for clarification
3. **VERIFY** — Check against codebase reality
4. **EVALUATE** — Technically sound for THIS domain/codebase?
5. **RESPOND** — Technical acknowledgment or reasoned pushback
6. **IMPLEMENT** — One item at a time, test each

**Never:** performative agreement, blind implementation, batch without testing.

**Push back if:** suggestion breaks existing functionality, lacks full context, violates YAGNI.

### Step 5: Produce Review Report
Write `REVIEW_ISSUES.md` with all findings categorized:
- Critical — must fix now
- Important — fix before proceeding
- Minor — note for later

### Step 6: If Flaws Detected — Apply Systematic Debugging

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

### Step 7: Fix Loop
- Found flaw → Execution Team debates fix → implements → Testing Agent re-validates
- `council-orchestrator loopback review "<reason>"` → re-run review → **GOTO LOOP step 1**
- Repeat until `REVIEW_ISSUES.md` has ZERO unresolved issues AND Testing Agent confirms zero test failures

### Step 8: Advance
`council-orchestrator advance review "all clear"` → **GOTO LOOP step 1**

---

## Stage 5 — VERIFY & DELIVER

### Uses: Testing Agent (final gate) + Head Agent (sign-off)

**Announce:** `## ✅ [Stage 5 — VERIFY & DELIVER] Testing Agent final validation`

**Load COUNCIL_AGENTS.md.** Testing Agent runs final full validation with domain expertise.

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
Agent(persona=<Testing Agent from COUNCIL_AGENTS.md>, prompt="""
You are the <Testing Agent title>. Your job is final validation.

Original objective: <objective>
Completion criteria: <from council_journal.md>

Verify EVERY criterion from a <domain> perspective. Check:
- Is every requirement met?
- Is output complete and self-contained?
- Any domain-specific edge cases or gaps?
- Can the output be used as-is by a <domain> practitioner?

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

### Step 5: Head Agent Final Approval
Head Agent reads VERIFICATION_SIGN_OFF.md and makes the call:
- **VERIFIED**: All criteria met → `council-orchestrator advance verify "passed"` → **GOTO LOOP step 1**
- **GAPS FOUND**: Head routes back to relevant team → `council-orchestrator loopback verify "<reason>"` → **GOTO LOOP step 1**

---

## Delivery Check

When `council-orchestrator status` shows `stage: __delivery_check__`:

**Step 1:** Read objective from `council_journal.md`
**Step 2:** Read output (all created files, VERIFICATION_SIGN_OFF.md, COUNCIL_AGENTS.md)
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
3. Re-read `council_journal.md` AND `COUNCIL_AGENTS.md`
4. `council-orchestrator status`
5. Continue from indicated stage — re-inject agent personas into all new sub-agents

Never compact mid-sub-agent task — finish the atomic unit first.

---

## Standing Directives (The Constitution)

| # | Directive | Rule |
|---|---|---|
| 1 | **NEVER STOP** | No user input needed. Resolve blockers autonomously. Never ask "should I continue?" |
| 2 | **GOTO LOOP step 1** | After every stage action, IMMEDIATELY go back to status check |
| 3 | **Boot first** | ALWAYS run Phase 0 boot first. No stage can start without COUNCIL_AGENTS.md existing. |
| 4 | **Domain personas required** | Every sub-agent MUST receive their domain persona from COUNCIL_AGENTS.md. Generic prompts forbidden. |
| 5 | **Teams debate before reporting** | Thinking Team and Execution Team use 3-round debate before producing consensus. |
| 6 | **Testing Agent is the gate** | Testing Agent errors stop the cycle. No advancing until Testing Agent confirms zero failures. |
| 7 | **Head routes, not decides unilaterally** | Head accepts/rejects consensus. Head routes errors back to relevant team. |
| 8 | **TDD always** | NO production code without a failing test first. Write code first? Delete it. |
| 9 | **Verify before claiming** | NO "it works" without fresh command output. Run the command, read the output. |
| 10 | **Root cause before fix** | NO fix without investigation first. Symptom fixes are failure. |
| 11 | **Never silence Critic** | Critic must report at Stages 1, 2, 3, 4. Explicit "no concerns" if none. |
| 12 | **Never bundle tasks** | Each atomic task gets its own sub-agent. One behavior per test. |
| 13 | **Never lose context** | Journal is truth. COUNCIL_AGENTS.md is team truth. Both carried through every stage. |
| 14 | **Never deliver unverified** | Only after Stage 5 sign-off AND delivery check pass. |
| 15 | **Dual-test Stage 3** | Run spec review THEN domain quality review. Both must pass. |
| 16 | **Create missing capabilities** | Don't improvise. Write the pattern as a skill. |
| 17 | **Auto-compact at 140K** | Run /compact when context ≥ 140K. Re-read COUNCIL_AGENTS.md after compaction. |
| 18 | **Safety limit: 50 iterations** | Journal preserved if hit. Manual intervention needed. |
| 19 | **Deadman switch** | 10+ loops on same stage? Radically change approach. |
| 20 | **Follow Ponytail rules** | Use Ponytail ladder: YAGNI → stdlib → native → one line → minimum. Avoid speculative abstractions/boilerplate. Mark shortcuts with `ponytail:` comments. |

---

## Embedded Skills — Quick Reference

This file IS the complete superpower library. All 14 patterns + domain agent system are embedded inline:

| Look For | Stage | Pattern Name | IRON LAW |
|---|---|---|---|
| **Generating domain agent team** | **Phase 0 — BOOT** | **Project Boot + Domain Detection** | **Boot before EVERYTHING. COUNCIL_AGENTS.md must exist.** |
| **Team collaboration** | **All stages** | **Team Debate Protocol** | **3-round debate before consensus. Head accepts/rejects.** |
| Exploring ideas, comparing architectures | 1 — THINK | Brainstorming (Thinking Team) | Thinking Team debates architecture. No singleton thinker. |
| Breaking down work into tasks | 2 — PLAN | Writing Plans (Thinking + Execution) | Execution Team validates plan feasibility. |
| Isolating work | 2 — PLAN | Git Worktrees | Work in isolation. No worktree on main branch. |
| Running independent tasks concurrently | 3 — CREATE | Parallel Dispatch (Executor A + B) | Executors run in parallel on independent task sets. |
| Task-by-task execution | 3 — CREATE | Subagent-Driven Dev (with personas) | Executor persona from COUNCIL_AGENTS.md in every sub-agent. |
| Writing code that works | 3 — CREATE | TDD | NO production code without a failing test first. |
| Missing capability during build | 3 — CREATE | Writing Skills | Write the pattern. Don't improvise. |
| Running all tests, finding all errors | 3 & 4 | Testing Agent Gate | Testing Agent: run all, report all, suppress nothing. |
| Reviewing code quality | 4 — REVIEW | Code Review (Critic + Testing Agent) | Domain-aware Critic + Testing Agent run simultaneously. |
| Routing errors to fix teams | 4 — REVIEW | Error Routing (Head → Execution Team) | Errors trigger Execution Team debate → fix → re-test. |
| Responding to feedback | 4 — REVIEW | Receiving Review | Verify before implementing. Push back if wrong. |
| Fixing bugs | 4 — REVIEW | Systematic Debugging | No fixes without root cause investigation first. |
| Confirming fixes | 4 & 5 | Verification Before Completion | No claims without fresh command output. |
| Merging, PR, finishing | 5 — VERIFY | Finishing Branch | Verify tests first. Then present options. |
| **Model discovery** | **Step 0** | **Live Model Catalog** | **Run `council-orchestrator models` before starting** |

---

## Activation

1. **Model discovery:** `council-orchestrator models`
2. **Announce:** `## 🔵 [Init] Council starting — domain-aware agent teams, all 14 patterns embedded inline`
3. **Initialize:** `council-orchestrator init "<full objective>"` ← starts at stage "boot"
4. **ENTER MAIN LOOP** — `council-orchestrator status` → stage will be "boot" → execute Phase 0

**Phase 0 runs first.** The council scans the project, detects the domain, generates the expert team, writes COUNCIL_AGENTS.md, then advances to "think". All subsequent stages use the domain-aware personas.

**The council is active. The team is being assembled. The loop is turning.**
