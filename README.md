# AI Council — Autonomous Orchestration Skills

A collection of universal skills for autonomous multi-agent orchestration using the **Head of AI Council** pattern.

## Skills

### [`council-orchestration`](./skills/council-orchestration/SKILL.md) ⭐ Universal / Single-Model

A self-governing 5-stage pipeline where **all agents run on your current active model** — no model switching, no external API dependencies. Works in Claude Code, Copilot CLI, Codex, and any CLI.

| Stage | Role |
|---|---|
| 1 — Think | Thinker sub-agent |
| 2 — Plan | Planner sub-agent |
| 3 — Create | Creator sub-agent |
| 4 — Review & Test | Reviewer sub-agent |
| 5 — Verify & Deliver | Verifier sub-agent |

**Use when:** autonomous end-to-end delivery needed, single active model only.

---

### [`ai-council-orchestration`](./skills/ai-council-orchestration/SKILL.md) Multi-Model

The original multi-model variant with explicit model assignments (GPT-5.5, Claude Opus, etc.).

**Use when:** you have access to multiple models and want specialized agents per stage.

---

## Installation

### Claude Code
```bash
git clone https://github.com/armaan-hub/AI-Coincil.git
cp -r AI-Coincil/skills/council-orchestration ~/.claude/skills/
```

### Copilot CLI (superpowers)
```bash
git clone https://github.com/armaan-hub/AI-Coincil.git
cp -r AI-Coincil/skills/council-orchestration \
  ~/.copilot/installed-plugins/superpowers-marketplace/superpowers/skills/
```

### Invoke
```
Use the skill tool to invoke "council-orchestration"
```
