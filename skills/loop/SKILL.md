---
name: loop
description: Cross-platform recurrent task runner — run any command on an interval (fixed or self-paced). Portable across Claude Code, Gemini CLI, Copilot CLI, and any shell.
---

# Loop — Cross-Platform Recurrent Task Runner

**Run any command on a recurring interval. Fixed or self-paced. Works everywhere.**

The `/loop` pattern lets you run a command, prompt, or skill repeatedly until a condition is met. Think `watch` for AI agents — but smarter, because each iteration carries full context from the previous one.

---

## Why This Exists

Claude Code has `/loop` as a built-in. Gemini CLI, Copilot CLI, Codex, and other AI CLIs don't — or have different mechanisms. This skill **standardizes the /loop pattern** so it works the same way everywhere. Each platform adapts to what it has natively, using this skill as the contract.

---

## How It Works

```
LOOP CONTRACT:
  1. Define WHAT to run:  any command, prompt, or skill name
  2. Define HOW OFTEN:    fixed interval (5m) or self-paced (dynamic)
  3. Define WHEN TO STOP: max iterations, condition check, or manual interrupt
  4. Run one iteration, persist state, schedule next, repeat
```

### State Management

A `loop_state.json` file tracks:
- `command` — what's being run
- `interval` — seconds between runs (0 = self-paced/dynamic)
- `iteration` — current run number
- `max_iterations` — safety limit (default: 9999)
- `last_run` — timestamp of last execution
- `history` — log of each iteration's outcome
- `condition` — optional stop condition check
- `active` — whether loop is running

---

## Platform Adaptation

### Claude Code

Two built-in mechanisms:

**Fixed interval — CronCreate (or ScheduleWakeup with fixed delay):**
```
/loop 5m /council-orchestration
/loop 30m "check deploy status"
/loop 10m /babysit-prs
```

**Self-paced — ScheduleWakeup (model decides interval):**
```
/loop /council-orchestration
/loop "fix failing tests"
/loop "monitor CI pipeline"
```

The model uses `ScheduleWakeup` tool with cache-aware delays (60s–3600s).

**To invoke this skill in Claude Code:**
```
/loop 5m /council-orchestration
/loop /council-orchestration
```

The built-in `/loop` command already handles this. Use this skill when you want the portable pattern explicitly.

### Gemini CLI

As of current Gemini CLI, recurrence works differently. Use this skill to implement the loop pattern:

**Option A — Shell-based (always works):**
```bash
# Install the loop.sh helper (installed by install.sh)
loop run "python orchestrator.py status" --interval 30 --max-iterations 10
```

**Option B — Self-paced (recommended for Gemini CLI):**
Invoke this skill, let the model decide when to loop back:
```
1. Run one iteration of /council-orchestration (or any command)
2. Use `activate_skill` to re-invoke this skill to check if we should continue
3. Loop back with accumulated context
```

**Gemini CLI specific flow:**
```
─── LOOP ITERATION 1 ───
  → Read the skill (this file)
  → Execute one iteration of your command
  → Use `activate_skill("loop", "status")` to persist state
  → Decide: continue? Then schedule next iteration via activate_skill again

─── LOOP ITERATION 2 ───
  → Skill reloads with context from iteration 1
  → Read loop_state.json for execution history
  → Execute next iteration
  → Repeat
```

### Copilot CLI

Copilot CLI uses the `skill` tool and subagent spawning:

**Subagent-per-iteration pattern:**
```
# Each iteration spawns a fresh subagent
Agent(
  description=f"Loop iteration {n}",
  prompt=f"Execute: <command>. Context from previous run: {context}"
)
```

**Cron-based (using system cron):**
```bash
# Use the loop.sh helper
loop run "gh copilot explain 'check status'" --interval 300
```

### Generic / Any Shell

The universal fallback — pure shell, zero dependencies:

```bash
# Basic watch loop (like `watch` but with state)
./loop.sh run "python orchestrator.py status" --interval 30

# Self-paced loop (press Enter to continue, Ctrl+C to stop)
./loop.sh interactive "python orchestrator.py status"

# Cron-based (writes crontab entry)
./loop.sh cron "python orchestrator.py status" --every "*/5 * * * *"
```

---

## The Loop Engine

Two helper scripts manage loop state:

### `loop.py` — Python Loop Engine

```bash
loop init "command" --interval 30 --max-iterations 100
loop status                    # Show current loop state
loop run                       # Execute one iteration
loop advance <outcome>         # Mark current iteration as done
loop schedule                  # Schedule next iteration (platform-aware)
loop stop                      # Halt the loop
loop history                   # Show full run log
loop cleanup                   # Remove loop state
```

### `loop.sh` — Shell Fallback (no Python needed)

```bash
loop run "command" --interval 30 --max-iterations 10
loop status
loop stop
```

---

## Using with AI Council

The loop skill integrates directly with the council orchestration:

```bash
# Self-paced council (model decides when to check back)
loop init "python orchestrator.py status && python orchestrator.py advance" --self-paced
loop run

# Fixed-interval council check-ins every 5 minutes
loop init "council-orchestrator status" --interval 300
loop run

# Loop the full council until objective met
loop init "Read program.md and execute the current council stage" --self-paced
loop run
```

---

## Standing Directives

| # | Directive |
|---|---|
| 1 | **CONTINUE UNTIL STOP CONDITION** — Don't ask "should I continue?" |
| 2 | **PERSIST STATE** — Always write loop_state.json after each iteration |
| 3 | **CARRY CONTEXT** — Each iteration starts with history from all previous runs |
| 4 | **RESPECT INTERVAL** — If fixed interval, don't run before the timer expires |
| 5 | **SELF-PACED** — If no interval, the model chooses: run now or schedule later |
| 6 | **MAX ITERATIONS** — Hard stop at configured limit (default 9999) |
| 7 | **PLATFORM-AWARE** — Use the best recurrence mechanism available on this platform |

---

## Quick Reference

| Action | Claude Code | Gemini CLI | Copilot CLI | Generic Shell |
|---|---|---|---|---|
| Fixed interval | `/loop 5m /cmd` | `loop run "cmd" -i 300` | `loop run "cmd" -i 300` | `loop.sh run "cmd" -i 300` |
| Self-paced | `/loop /cmd` | `activate_skill("loop")` per iteration | Subagent per iteration | `loop.sh interactive "cmd"` |
| status | `loop status` | `loop status` | `loop status` | `loop.sh status` |
| stop | `loop stop` | `loop stop` | `loop stop` | `loop.sh stop` |

---

**The loop is turning. Each iteration brings progress. Never stop until the condition is met.**
