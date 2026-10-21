# AI Council — Autonomous Program

This is the master program file. It contains everything an AI agent needs to run the
council autonomously. Point your Claude Code / Copilot CLI / Codex here and let it go.

## What Makes This Council Different

Before any work begins, the council **scans your project, detects the domain, and assembles a team of domain-appropriate expert agents**. A legal project gets lawyers. A medical system gets doctors. A cooking app gets chefs. The agent team is written to `COUNCIL_AGENTS.md` and all subsequent stages use those domain-specific personas.

**Integrated from [karpathy/autoresearch](https://github.com/karpathy/autoresearch):**
- **Keep/Discard Protocol** — After every CREATE, measure a success metric. Improved → KEEP. Regressed → DISCARD (rollback changes) and loop back to THINK.
- **Experiment Log** — Every iteration's outcome recorded in `EXPERIMENT_LOG.md`. View with `council-orchestrator experiment`.
- **Lightweight Mode** — `init --light` for simple tasks (skip multi-agent debate, use Karpathy-style minimal loop).
- **Analysis Report** — Post-run analysis generated with `council-orchestrator analysis`.

**Built-in Ponytail (KISS/YAGNI):**
- Over-engineering prevention at every stage using the Ponytail ladder: YAGNI → stdlib → native → one line → minimum code.
- Standalone commands also available: `/ponytail`, `/ponytail-review`, `/ponytail-audit`, etc.

**Agent hierarchy (full mode):**
- 👑 **Head Agent** — Orchestrates all, routes tasks, accepts/rejects consensus
- 🧠 **Thinking Team** (2 agents) — Domain strategists who debate before proposing
- ⚒️ **Execution Team** (2 agents) — Domain builders who implement and debate fixes
- 🔍 **Critic Agent** — External domain challenger who assumes work is wrong
- 🧪 **Testing Agent** — Domain verifier who runs all tests and reports to Head

**Agent hierarchy (lightweight mode):**
- 👑 **Head Agent** — Orchestrates, routes, approves
- ⚒️ **Creator** — Single agent who proposes and implements
- 🧪 **Testing Agent** — Verifies all outputs

## Human: Define Your Success Metric

To enable the Keep/Discard protocol, define a success measure:

```
Success metric: [metric name, e.g. "test pass rate"]
Direction:      [lower/higher is better]
Target value:   [e.g. 100%]
```

Examples:
- `test pass rate` (higher is better) — for code tasks
- `val_bpb` (lower is better) — for ML training (Karpathy style)
- `lint count` (lower is better) — for refactoring
- `coverage %` (higher is better) — for testing tasks

If no metric is given, the default is "completion criteria satisfied."

## Setup

1. Read this entire `program.md` file
2. Read `orchestrator.py` — the state management engine
3. Read `skills/council-orchestration/SKILL.md` — the full orchestration instructions
4. Choose mode:
   - **Full:** `python orchestrator.py init "<your objective>"`
   - **Lightweight:** `python orchestrator.py --light init "<your objective>"`
5. Status will show `stage: boot` — execute Phase 0 (Project Boot) first
6. The council is now active and self-driving

## Quick Start

```bash
# Full mode — multi-agent with debate
python orchestrator.py init "Implement a Redis-backed rate limiter with configurable windows"

# OR Lightweight mode — simple, no debate (Karpathy-style)
python orchestrator.py --light init "Fix the login button alignment"

# Check status — will show "stage: boot"
python orchestrator.py status

# Execute Phase 0: scan project, detect domain, generate COUNCIL_AGENTS.md
# (follow SKILL.md Phase 0 instructions)

# After boot → stage advances to "think" automatically
# Check your team
python orchestrator.py agents

# Continue the loop from "think"
python orchestrator.py status

# After CREATE stage — use Keep/Discard protocol:
python orchestrator.py keep "test pass: 100%"    # Metric improved → continue
python orchestrator.py discard "val_bpb: 1.89"    # Metric regressed → rollback

# View experiment log anytime:
python orchestrator.py experiment

# Generate analysis on delivery:
python orchestrator.py analysis
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
9. **Apply Ponytail** — follow the ladder: YAGNI → stdlib → native → one line → minimum code
10. **DELIVER** — when objective is satisfied, present the final output

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

**Lightweight mode** skips plan and review stages — advance immediately when those stages appear.

## Key Files Generated

| File | Purpose |
|---|---|
| `COUNCIL_AGENTS.md` | Domain-aware agent personas (generated in Phase 0, used in all stages) |
| `council_journal.md` | Full state machine and history |
| `THOUGHT_REPORT.md` | Architecture analysis from Thinking Team |
| `TEAM_CONSENSUS.md` | Team debate outcomes |
| `TASK_EXECUTION_PLAN.md` | Execution Team task breakdown |
| `EXPERIMENT_LOG.md` | Keep/Discard experiment tracking |
| `REVIEW_ISSUES.md` | Critic findings |
| `TEST_RESULTS.md` | Testing Agent output |
| `VERIFICATION_SIGN_OFF.md` | Final verification |
| `ANALYSIS_REPORT.md` | Post-run analysis |

## What to Check After Each Stage

After `python orchestrator.py advance <stage>`:
- Run status again to confirm the next stage
- If something is wrong, use `python orchestrator.py loopback <stage> "<reason>"`
- Then immediately execute the loopback stage

## The NEVER STOP Rule

Inspired by autoresearch: **the council does not ask for permission between stages.** It resolves blockers autonomously. If output doesn't meet the objective, it loops back with accumulated learnings and tries again. The loop stops only when:

1. The objective is fully satisfied — output delivered ✅
2. The safety limit (50 iterations) is hit — journal preserved for review ⚠️
3. You manually interrupt the session 🛑

## Output

When the objective is satisfied:
1. Run `python orchestrator.py status` to confirm `__delivery_check__`
2. Run `python orchestrator.py analysis` to generate the analysis report
3. Present a clean summary of what was built/achieved
4. Include paths to all created artifacts
5. The journal (`council_journal.md`) and agent team (`COUNCIL_AGENTS.md`) contain the full history
