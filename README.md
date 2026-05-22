# AI Council — Autonomous Orchestration Skills

A collection of universal skills for autonomous multi-agent orchestration using the **Head of AI Council** pattern.

## Skills

### [`ai-council-orchestration`](./skills/ai-council-orchestration/SKILL.md)

A self-governing multi-agent pipeline that executes any complex objective autonomously across 5 strict stages:

| Stage | Agent | Model |
|---|---|---|
| 1 — Think | Thinker | GPT-5.5 |
| 2 — Plan | Planner | GPT-5.4 |
| 3 — Create | Creator | GPT-5.3-Codex |
| 4 — Review & Test | Reviewer & Tester | Claude Opus 4.7 |
| 5 — Verify & Deliver | Verifier | Claude Sonnet 4.6 |

**Use when:** facing any complex multi-step objective requiring autonomous end-to-end delivery without user intervention.

## Usage

Copy the skill to your agent's skills directory:

\`\`\`bash
# For Claude Code
cp skills/ai-council-orchestration/SKILL.md ~/.claude/skills/ai-council-orchestration/SKILL.md

# For Copilot CLI (superpowers)
cp skills/ai-council-orchestration/SKILL.md \
  ~/.copilot/installed-plugins/superpowers-marketplace/superpowers/skills/ai-council-orchestration/SKILL.md
\`\`\`

Then invoke in any session:
\`\`\`
Use the skill tool to invoke "ai-council-orchestration"
\`\`\`
