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

## Files

| File | Purpose |
|---|---|
| [`program.md`](./program.md) | The autoresearch-style program — point your agent here to launch the council |
| [`orchestrator.py`](./orchestrator.py) | State management engine — tracks stage, iteration, loops, completion criteria |
| [`skills/council-orchestration/SKILL.md`](./skills/council-orchestration/SKILL.md) | Full orchestration instructions for single-model mode |
| [`skills/ai-council-orchestration/SKILL.md`](./skills/ai-council-orchestration/SKILL.md) | Full orchestration instructions for multi-model mode |
| [`install.sh`](./install.sh) | Install skills into Claude Code / Copilot CLI |

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
