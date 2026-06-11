# AI Council — Autonomous Program

This is the master program file. It contains everything an AI agent needs to run the
council autonomously. Point your Claude Code / Copilot CLI / Codex here and let it go.

## What Makes This Council Different

Before any work begins, the council **scans your project, detects the domain, and assembles a team of domain-appropriate expert agents**. A legal project gets lawyers. A medical system gets doctors. A cooking app gets chefs. The agent team is written to `COUNCIL_AGENTS.md` and all subsequent stages use those domain-specific personas.

**Agent hierarchy:**
- 👑 **Head Agent** — Orchestrates all, routes tasks, accepts/rejects consensus
- 🧠 **Thinking Team** (2 agents) — Domain strategists who debate before proposing
- ⚒️ **Execution Team** (2 agents) — Domain builders who implement and debate fixes
- 🔍 **Critic Agent** — External domain challenger who assumes work is wrong
- 🧪 **Testing Agent** — Domain verifier who runs all tests and reports to Head

## Setup

1. Read this entire `program.md` file
2. Read `orchestrator.py` — the state management engine
3. Read `skills/council-orchestration/SKILL.md` — the full orchestration instructions
4. Run `python orchestrator.py init "<your objective>"`
5. Status will show `stage: boot` — execute Phase 0 (Project Boot) first
6. The council is now active and self-driving

## Quick Start

```bash
# Set your objective
python orchestrator.py init "Implement a Redis-backed rate limiter with configurable windows"

# Check status — will show "stage: boot"
python orchestrator.py status

# Execute Phase 0: scan project, detect domain, generate COUNCIL_AGENTS.md
# (follow SKILL.md Phase 0 instructions)

# After boot → stage advances to "think" automatically
# Check your team
python orchestrator.py agents

# Continue the loop from "think"
python orchestrator.py status
```

### Recurrence via Loop

Use the `/loop` skill to run the council on a recurring schedule:

```bash
# Self-paced — model decides when to check back
loop run "python orchestrator.py status"

# Fixed interval — check every 5 minutes
loop run "python orchestrator.py status" --interval 300

# Shell fallback (no Python)
./loop.sh run "python orchestrator.py status" --interval 300
```

## What the AI Does

You are the **Council Head**. Your job:

1. **Run the main loop** — never stop, never ask for permission
2. **Phase 0 first** — always execute boot stage before any work begins
3. **Read COUNCIL_AGENTS.md** before every stage — inject domain personas into all sub-agents
4. **At each stage**, read the council-orchestration skill and follow its instructions precisely
5. **All 14 superpower patterns + domain agent system are embedded inline** — no external Skill calls needed
6. **Check state** (`python orchestrator.py status`) before every action
7. **Advance or loopback** based on stage outcomes
8. **PERSIST** — write every report to disk (COUNCIL_AGENTS.md, THOUGHT_REPORT.md, TASK_EXECUTION_PLAN.md, etc.)
9. **DELIVER** — when objective is satisfied, present the final output

## Loop Behavior

```
python orchestrator.py status
→ If "stage: boot":        run Phase 0 (scan project → infer domain → generate COUNCIL_AGENTS.md → advance)
→ If "stage: think":       run Stage 1 (Thinking Team debates → Critic challenges → Head approves → advance)
→ If "stage: plan":        run Stage 2 (Thinking Team plans → Execution Team validates → Critic challenges → advance)
→ If "stage: create":      run Stage 3 (Execution Team builds TDD → Testing Agent gates → advance)
→ If "stage: review":      run Stage 4 (Critic + Testing Agent parallel review → errors routed to Execution Team → advance)
→ If "stage: verify":      run Stage 5 (Testing Agent final validation → Head sign-off → advance)
→ If "__delivery_check__": check if objective met → deliver OR loop
→ If "__maxed_out__":      output summary — safety limit reached
```

## Key Files Generated

| File | Purpose |
|---|---|
| `COUNCIL_AGENTS.md` | Domain-aware agent personas (generated in Phase 0, used in all stages) |
| `council_journal.md` | Full state machine and history |
| `THOUGHT_REPORT.md` | Architecture analysis from Thinking Team |
| `TEAM_CONSENSUS.md` | Team debate outcomes |
| `TASK_EXECUTION_PLAN.md` | Execution Team task breakdown |
| `REVIEW_ISSUES.md` | Critic findings |
| `TEST_RESULTS.md` | Testing Agent output |
| `VERIFICATION_SIGN_OFF.md` | Final verification |

## What to Check After Each Stage

After `python orchestrator.py advance <stage>`:
- Run status again to confirm the next stage
- If something is wrong, use `python orchestrator.py loopback <stage> "<reason>"`
- Then immediately execute the loopback stage

## The NEVER STOP Rule

- Do NOT ask "should I continue?" or "is this good enough?"
- Do NOT wait for user confirmation between stages
- If blocked, try a different approach, not a different person
- If stuck on the same stage for 10+ loops, radically change the approach
- If all approaches exhausted, document in journal and deliver best effort
- **ALWAYS use domain personas from COUNCIL_AGENTS.md — never spawn generic agents**

## Output

When the objective is satisfied:
1. Run `python orchestrator.py status` to confirm `__delivery_check__`
2. Present a clean summary of what was built/achieved
3. Include paths to all created artifacts
4. The journal (`council_journal.md`) and agent team (`COUNCIL_AGENTS.md`) contain the full history
