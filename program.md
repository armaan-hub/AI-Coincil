# AI Council — Autonomous Program

This is the master program file. It contains everything an AI agent needs to run the
council autonomously. Point your Claude Code / Copilot CLI / Codex here and let it go.

## Setup

1. Read this entire `program.md` file
2. Read `orchestrator.py` — the state management engine
3. Read `skills/council-orchestration/SKILL.md` — the full orchestration instructions
4. Run `python orchestrator.py init "<your objective>"`
5. The council is now active and self-driving

## Quick Start

```bash
# Set your objective
python orchestrator.py init "Implement a Redis-backed rate limiter with configurable windows"

# Check status
python orchestrator.py status

# If the orchestrator says "stage: think" — start at Stage 1
# If it says something else — start at the indicated stage
```

## What the AI Does

You are the **Council Head**. Your job:

1. **Run the main loop** — never stop, never ask for permission
2. **At each stage**, read the council-orchestration skill and follow its instructions precisely
3. **All 14 superpower patterns are embedded inline** — no external Skill calls needed. The patterns are part of the SKILL.md file itself.
4. **Check state** (`python orchestrator.py status`) before every action
5. **Advance or loopback** based on stage outcomes
6. **PERSIST** — write every report to disk (THOUGHT_REPORT.md, TASK_EXECUTION_PLAN.md, etc.)
7. **DELIVER** — when objective is satisfied, present the final output

## Loop Behavior

```
python orchestrator.py status
→ If "stage: think":       run Stage 1 (embedded Brainstorming Pattern → Thinker → Critic → advance)
→ If "stage: plan":        run Stage 2 (embedded Writing Plans Pattern → Planner → Critic → advance)
→ If "stage: create":      run Stage 3 (embedded TDD + Subagent + Parallel Patterns → Critic → advance)
→ If "stage: review":      run Stage 4 (embedded Code Review + Debug Patterns → advance)
→ If "stage: verify":      run Stage 5 (embedded Verification + Branch Finishing Patterns → advance)
→ If "__delivery_check__": check if objective met → deliver OR loop
→ If "__maxed_out__":      output summary — safety limit reached
```

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

## Output

When the objective is satisfied:
1. Run `python orchestrator.py status` to confirm `__delivery_check__`
2. Present a clean summary of what was built/achieved
3. Include paths to all created artifacts
4. The journal (`council_journal.md`) contains the full history
