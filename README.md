# AI Council — Autonomous Orchestration Skills

A self-looping, never-stopping multi-agent orchestration system inspired by [Karpathy's autoresearch](https://github.com/karpathy/autoresearch.git).

**The council cycles through 5 stages (Think → Plan → Create → Review → Verify) in an autonomous loop. All 14 superpower patterns are embedded inline — zero external Skill dependencies. The loop runs until the objective is fully resolved.**

## Architecture

```
┌─────────────────────────────────────────────���───────────────────┐
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

## Skills

### [`council-orchestration`](./skills/council-orchestration/SKILL.md) ⭐ Single-Model

All agents run on your current active model. No model switching needed. Works in any CLI.

| Stage | Embedded Patterns Used |
|---|---|
| **1 — Think** | Brainstorming Pattern + Critic (embedded inline) |
| **2 — Plan** | Writing Plans Pattern (embedded inline) |
| **3 — Create** | TDD + Subagent-Driven Dev + Parallel Dispatch (all embedded inline) |
| **4 — Review & Test** | Code Review + Systematic Debugging (embedded inline) |
| **5 — Verify & Deliver** | Verification + Finishing Branch (embedded inline) |

### [`ai-council-orchestration`](./skills/ai-council-orchestration/SKILL.md) Multi-Model

Same loop, but switches to the best model per stage (Claude Opus for thinking, Sonnet for planning, etc.).

### [`loop`](./skills/loop/SKILL.md) 🔁 Cross-Platform Recurrent Task Runner

Run any command on a recurring interval — fixed or self-paced. Works across Claude Code, Gemini CLI, Copilot CLI, and plain shell.

**Adapts to the platform:** Claude Code uses `ScheduleWakeup`, Gemini CLI uses `activate_skill` chaining, Copilot CLI uses subagent dispatch, and the shell fallback uses watch/cron.

| Mechanism | Claude Code | Gemini CLI | Copilot CLI | Any Shell |
|---|---|---|---|---|
| Fixed interval | `/loop 5m /cmd` | `loop run "cmd" -i 30` | `loop run "cmd" -i 30` | `./loop.sh run "cmd" -i 30` |
| Self-paced | `/loop /cmd` | `activate_skill("loop")` | subagent loop | `./loop.sh interactive "cmd"` |
| Status | `loop status` | `loop status` | `loop status` | `./loop.sh status` |

### [`ponytail`](./skills/ponytail/SKILL.md) 🦎 Over-Engineering Prevention (KISS/YAGNI)

Forces the simplest, shortest solution that actually works: standard library first, native platform features before dependencies, and one line before fifty. Fully embedded in the Thinking, Planning, Creating, and Reviewing stages of the AI Council.

| Command | What it does |
|---------|--------------|
| `/ponytail [lite \| full \| ultra \| off]` | Set the intensity, or turn it off. No argument reports the current level. |
| `/ponytail-review` | Review the current diff for over-engineering, hands back a delete-list. |
| `/ponytail-audit` | Audit the whole repo for over-engineering, not just the diff. |
| `/ponytail-debt` | Harvest the ponytail: shortcuts you've deferred into a ledger, so "later" doesn't become "never". |
| `/ponytail-gain` | Show the measured impact scoreboard (less code, less cost, more speed) from the benchmark. |
| `/ponytail-help` | Quick reference for the commands above. |

## Files

| File | Purpose |
|---|---|
| [`program.md`](./program.md) | The autoresearch-style program — point your agent here to launch the council |
| [`orchestrator.py`](./orchestrator.py) | State management engine — tracks stage, iteration, loops, completion criteria |
| [`loop.py`](./loop.py) | Cross-platform loop state engine (Python) |
| [`loop.sh`](./loop.sh) | Loop engine shell fallback (zero deps) |
| [`AGENTS.md`](./AGENTS.md) | Global developer ruleset enforcing KISS/YAGNI guidelines |
| [`skills/council-orchestration/SKILL.md`](./skills/council-orchestration/SKILL.md) | Full orchestration instructions (Single-Model) with embedded Ponytail rules |
| [`skills/ai-council-orchestration/SKILL.md`](./skills/ai-council-orchestration/SKILL.md) | Full orchestration instructions (Multi-Model) with embedded Ponytail rules |
| [`skills/loop/SKILL.md`](./skills/loop/SKILL.md) | Cross-platform loop skill definition |
| [`skills/ponytail/SKILL.md`](./skills/ponytail/SKILL.md) | Standard Ponytail over-engineering prevention guidelines |
| [`skills/ponytail-review/SKILL.md`](./skills/ponytail-review/SKILL.md) | Instruction for over-engineering reviews |
| [`skills/ponytail-audit/SKILL.md`](./skills/ponytail-audit/SKILL.md) | Whole-repo over-engineering audits |
| [`skills/ponytail-debt/SKILL.md`](./skills/ponytail-debt/SKILL.md) | Debt ledger compiler |
| [`skills/ponytail-gain/SKILL.md`](./skills/ponytail-gain/SKILL.md) | Scoreboard viewer |
| [`skills/ponytail-help/SKILL.md`](./skills/ponytail-help/SKILL.md) | Command quick reference |
| [`install.sh`](./install.sh) | Install AI Council and Ponytail skills into Claude Code / Copilot CLI / PATH |

## Quick Start

### 1. Install the skills

```bash
bash install.sh
```

### 2. Start the council

In Claude Code, invoke:

```
/council-orchestration
```

Or use the program.md pattern (like autoresearch):

```
Hi, read program.md and let's kick off a new council session. I want you to: <your objective>
```

### 3. Let it loop

The council runs autonomously:
- **Stage 1:** Thinks deeply, explores architectures, stress-tests assumptions
- **Stage 2:** Plans implementation in atomic tasks with success criteria
- **Stage 3:** Creates code using TDD, parallel agents, and dual-testing
- **Stage 4:** Reviews everything, debugs systematically, verifies fixes
- **Stage 5:** Verifies end-to-end, confirms objective satisfaction
- **Delivery check:** If satisfied → delivers. If not → loops back to Stage 1

**You do not need to supervise.** The council loops until the objective is met or you interrupt it.

### 4. Monitor progress

```bash
python orchestrator.py status     # Current stage, iteration, loop count
python orchestrator.py history    # Full history of all stages and decisions
```

## The NEVER STOP Rule

Inspired by autoresearch: **the council does not ask for permission between stages.** It resolves blockers autonomously. If output doesn't meet the objective, it loops back with accumulated learnings and tries again. The loop stops only when:

1. The objective is fully satisfied — output delivered ✅
2. The safety limit (50 iterations) is hit — journal preserved for review ⚠️
3. You manually interrupt the session 🛑

## Installation

### Claude Code

```bash
git clone https://github.com/armaan-hub/AI-Coincil.git
cp -r AI-Coincil/skills/council-orchestration ~/.claude/skills/
```

Then invoke with `/council-orchestration`.

### Copilot CLI (superpowers)

```bash
git clone https://github.com/armaan-hub/AI-Coincil.git
cp -r AI-Coincil/skills/council-orchestration \
  ~/.copilot/installed-plugins/superpowers-marketplace/superpowers/skills/
```

### Or use the installer

```bash
bash install.sh
```

---

**The council is active. The loop is turning. Awaiting the objective.**
