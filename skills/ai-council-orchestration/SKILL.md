---
name: ai-council-orchestration
description: Multi-model autonomous loop through Think→Plan→Create→Review→Verify — uses the best model per stage from ALL connected providers. Live auto-discovery of available models.
---

# AI Council Orchestration — Multi-Model, All Providers

**Every stage uses the best available model for its role.** Model catalog is auto-discovered at runtime — no hardcoded model names that go stale. Works with GitHub Copilot, OpenCode Zen, Nvidia NIM, Ollama, Gemini, OpenAI, Groq, OpenRouter, and official Claude.

## Quick Start

```bash
council-orchestrator models                   # Step 0: discover available models
council-orchestrator init "<your objective>"   # Step 1: start council
council-orchestrator status                    # Step 2: check stage
```

Then enter the loop below.

## Model Discovery (Step 0)

**Before entering the main loop, run:**
```bash
council-orchestrator models
```
This queries `http://127.0.0.1:4001/v1/models` live and writes `COUNCIL_MODELS.md` with:
- All available models grouped by provider
- Recommended model for each council role
- Live indicators (⚡ = connected now)

If the proxy isn't running, fall back to the embedded catalog below.

## Role-to-Model Mapping (Live)

| Role | Best Picks (in priority order) | Selection Strategy |
|---|---|---|
| **Thinker** (deep reasoning) | copilot/claude-opus-4.6-1m → opencode/qwen3.7-max → opencode/deepseek-v4-pro → opencode/kimi-k2.6 | Strongest analytical model available |
| **Planner** (task decomposition) | copilot/claude-sonnet-4.6 → opencode/qwen3.6-plus → opencode/minimax-m2.7 | Best at structured planning |
| **Creator** (code + TDD) | copilot/gpt-5.4 → opencode/deepseek-v4-flash → opencode/minimax-m2.7 → copilot/grok-code-fast-1 | Best code generation available |
| **Critic** (adversarial review) | copilot/claude-sonnet-4.6 → opencode/deepseek-v4-pro → opencode/kimi-k2.6 | Strong at finding flaws |
| **Reviewer** (code review) | copilot/claude-sonnet-4.6 → opencode/qwen3.6-plus → opencode/minimax-m2.5 | Balanced review quality |
| **Verifier** (fast checks) | copilot/claude-haiku-4.5 → copilot/gpt-5-mini → opencode/deepseek-v4-flash-free | Fast & cheap, uses FREE tier if available |

**Selection rule:** Pick the first model from the priority list that is currently connected (⚡ in `council-orchestrator models` output). If none of the top picks are available, use **any connected model** — don't stall.

---

## Embedded Model Catalog (Fallback)

If the proxy is unreachable, use this static reference:

### GitHub Copilot (connected ✅)
| Model ID | Capabilities | Best For |
|---|---|---|
| copilot/claude-opus-4.6-1m | Vision, 15x premium | ★ Thinker, Critic |
| copilot/claude-sonnet-4.6 | Vision | ★ Planner, Reviewer, Critic |
| copilot/claude-sonnet-4.5 | Vision | Reviewer, Planner |
| copilot/claude-haiku-4.5 | Vision, 0.33x cost | ★ Verifier |
| copilot/gpt-5.4 | Vision | ★ Creator |
| copilot/gpt-5.2 | Vision | Creator |
| copilot/gpt-5-mini | Vision, **FREE** | Verifier, Critic, fallback |
| copilot/grok-code-fast-1 | Fast coding | Creator (fast path) |

### OpenCode Zen (always available ✅)
| Model ID | Context | Best For |
|---|---|---|
| opencode/minimax-m3 | 128K | All-rounder |
| opencode/minimax-m2.7 | **1M ctx** | ★ Planner (large codebases) |
| opencode/minimax-m2.5 | **1M ctx** | Large context tasks |
| opencode/qwen3.7-max | 128K | ★ Thinker, Creator |
| opencode/qwen3.7-plus | 128K | Creator |
| opencode/qwen3.6-plus | 131K | ★ Planner, Reviewer |
| opencode/qwen3.5-plus | 131K | All-rounder |
| opencode/kimi-k2.6 | 131K | ★ Thinker, Critic |
| opencode/kimi-k2.5 | 131K | Thinker, Critic |
| opencode/deepseek-v4-pro | 65K | ★ Thinker, Critic |
| opencode/deepseek-v4-flash | 65K | ★ Creator (fast) |
| opencode/glm-5.1 | 128K | All-rounder |
| opencode/glm-5 | 128K | All-rounder |
| opencode/mimo-v2.5-pro | 262K | Large context |
| opencode/mimo-v2.5 | 262K | Large context |
| opencode/mimo-v2-pro | 65K | General |
| opencode/mimo-v2-omni | 65K | General |
| opencode/hy3-preview | 131K | Preview |

### OpenCode Zen — FREE tier (always available ✅)
| Model ID | Best For |
|---|---|
| opencode/deepseek-v4-flash-free | ★ Verifier, fallback Creator |
| opencode/mimo-v2.5-free | Verifier, fallback |
| opencode/minimax-m3-free | Verifier, fallback |
| opencode/nemotron-3-super-free | Verifier, fallback |

### Nvidia NIM (if connected)
meta/llama-3.3-70b-instruct, meta/llama-3.1-8b-instruct, nvidia/llama-3.1-nemotron-70b-instruct, nvidia/nemotron-3-ultra-550b-a55b, mistralai/mistral-7b-instruct-v0.3

### Ollama (local, if running)
qwen3:8b, qwen3:14b, llama3.3:70b

### Google Gemini (if connected)
gemini-2.5-pro, gemini-2.5-flash, gemini-2.0-flash, gemini-1.5-pro, gemini-1.5-flash

### OpenAI (if connected)
gpt-4o, gpt-4o-mini, o3-mini, o4-mini, gpt-4.1, codex-mini-latest

### Groq (if connected)
llama-3.3-70b-versatile, llama-3.1-8b-instant, deepseek-r1-distill-llama-70b, mixtral-8x7b, gemma2-9b-it

### OpenRouter (if connected)
google/gemma-3-27b-it:free, meta-llama/llama-3.3-70b-instruct:free, deepseek/deepseek-r1:free, qwen/qwen3-8b:free

### Claude (Anthropic, official — if not using proxy)
claude-sonnet-4-6, claude-sonnet-4-5, claude-haiku-4-5, claude-opus-4-7, claude-opus-4-6, claude-opus-4-5

---

## Architecture

```
STEP 0: council-orchestrator models     ← discover available models (live)

LOOP:
  1. council-orchestrator status        ← check current stage
  2. Select best model for stage         ← pick from connected providers
  3. Execute stage handler               ← uses embedded patterns below
  4. council-orchestrator advance/loopback ← update state
  5. GOTO step 1                        ← UNCONDITIONAL

BREAK ONLY when:
  - __delivery_check__ says done → DELIVER
  - __maxed_out__ safety limit → REPORT
```

## Council Structure

| Agent | Role | Model Selection Strategy |
|---|---|---|
| **Thinker** | Deep reasoning, ideation | Pick strongest analytical model connected |
| **Planner** | Task decomposition, file mapping | Best at structured breakdown |
| **Creator** | Implementation + TDD | Best code generator connected |
| **Critic** | Adversarial review | Strong analysis, find flaws |
| **Reviewer** | Code review | Balanced, thorough |
| **Verifier** | Fast final verification | Fastest/cheapest connected |

---

## Stage 1 — THINK

**Embedded: Brainstorming Pattern**

**Model: Strongest analytical model connected** (priority: copilot/claude-opus-4.6-1m → opencode/qwen3.7-max → opencode/deepseek-v4-pro → opencode/kimi-k2.6 → any connected)

1. **Model selection:** Run `council-orchestrator models` or check `COUNCIL_MODELS.md`. Pick the best Thinker model from what's connected.
2. **Explore context & load helper skills** — read project files, docs, recent commits. Also read and load all helper skills (`skills/ponytail/SKILL.md`, `skills/ponytail-review/SKILL.md`, `skills/ponytail-audit/SKILL.md`, `skills/ponytail-debt/SKILL.md`, `skills/ponytail-gain/SKILL.md`, `skills/ponytail-help/SKILL.md`, `skills/loop/SKILL.md`) to integrate their rules and capabilities into the session context.
3. **Clarify & decompose** — break objective into independent subsystems.
4. **Propose 2-3 architectures** with explicit trade-offs (adhering to Ponytail rules: YAGNI, standard library/native features first, no speculative abstractions).
5. **Stress-test:** What assumptions could be false? What could go wrong?
6. **Spawn Thinker sub-agent** → `THOUGHT_REPORT.md`
7. **Spawn Critic sub-agent** → `CRITIQUE_REPORT.md`
8. If concerns → `council-orchestrator loopback think "<reason>"` → **GOTO LOOP**
9. If clear → `council-orchestrator advance think "approved"` → **GOTO LOOP**

## Stage 2 — PLAN

**Embedded: Writing Plans Pattern**

**Model: Best planner connected** (priority: copilot/claude-sonnet-4.6 → opencode/qwen3.6-plus → opencode/minimax-m2.7 → best connected)

1. **Model selection:** Pick the best Planner model.
2. Map the absolute minimum file structure needed. Avoid speculative helper files or interfaces.
3. Decompose into bite-sized tasks (2-5 min each).
4. Write `TASK_EXECUTION_PLAN.md` with real code in every step. No placeholders or boilerplate.
5. Self-review: spec coverage? placeholders? type consistency?
6. Spawn Critic: missing criteria? dependencies correct?
7. If concerns → loopback → **GOTO LOOP**
8. If clear → advance → **GOTO LOOP**

## Stage 3 — CREATE

**Embedded: TDD + Subagent-Driven Development + Parallel Dispatch Patterns**

**Model: Best coder connected** (priority: copilot/gpt-5.4 → opencode/deepseek-v4-flash → opencode/minimax-m2.7 → copilot/grok-code-fast-1 → any connected)

1. **Model selection:** Pick the best Creator model. Verify current level using `/ponytail`.
2. **TDD IRON LAW:** No production code without a failing test first.
3. RED → Verify RED → GREEN (minimal implementation following Ponytail ladder: YAGNI → stdlib → native → one-line → minimum code) → Verify GREEN → REFACTOR (staying green, mark simplifications with `ponytail:` comments).
4. Dispatch fresh sub-agents per independent task. Ensure they are instructed to follow the Ponytail ladder.
5. Two-stage review per task: spec compliance → code quality.
6. Parallel dispatch for independent domains.
7. If missing capability → write pattern as skill.
8. If done → advance → **GOTO LOOP**
9. If issues → loopback → **GOTO LOOP**

## Stage 4 — REVIEW & TEST

**Embedded: Code Review + Systematic Debugging + Verification Patterns**

**Model: Best reviewer connected** (priority: copilot/claude-sonnet-4.6 → opencode/deepseek-v4-pro → opencode/qwen3.6-plus → any connected)

1. **Model selection:** Pick the best Reviewer model.
2. Pre-review: get SHAs, summary of what was built.
3. Spawn ALL council roles to review simultaneously. Critic must run a ponytail-review for over-engineering (tags: delete, stdlib, native, yagni, shrink) and report net lines removable.
   Additionally, run the `/ponytail-review` command (or `ponytail-review` skill) directly on the current git diff to harvest a concrete delete-list.
4. If flaws → Systematic Debugging (4-phase: root cause → pattern → hypothesis → fix)
5. **IRON LAW:** No fixes without root cause investigation.
6. Fix → re-verify → loopback review → **GOTO LOOP**
7. When clean → advance → **GOTO LOOP**

## Stage 5 — VERIFY & DELIVER

**Embedded: Verification Before Completion + Finishing Branch Patterns**

**Model: Fastest/cheapest connected** (priority: copilot/claude-haiku-4.5 → copilot/gpt-5-mini → opencode/deepseek-v4-flash-free → any FREE model)

1. **Model selection:** Pick the cheapest available model — verification is simple checks.
2. **IRON LAW:** No "it works" without fresh verification output.
3. Run full test suite, build, integration.
4. Spawn completeness verifier.
5. Run the `/ponytail-debt` command (or `ponytail-debt` skill) to harvest any deferred shortcuts into `PONYTAIL-DEBT.md`.
6. Produce `VERIFICATION_SIGN_OFF.md`.
7. If verified → advance → **GOTO LOOP**
7. If not → loopback to appropriate stage → **GOTO LOOP**

## Delivery Check

When stage is `__delivery_check__`:
- If objective satisfied → DELIVER. **STOP THE LOOP.**
- If not → `council-orchestrator next-iteration` → **GOTO LOOP**

## Standing Directives

| # | Directive | Rule |
|---|---|---|
| 1 | **NEVER STOP** | No user input needed. Resolve blockers autonomously. |
| 2 | **GOTO LOOP step 1** | After every action, immediately check status |
| 3 | **TDD always** | No production code without a failing test first |
| 4 | **Verify before claiming** | Run command, check fresh exit code & output |
| 5 | **Root cause before fix** | No symptom fixes without investigation |
| 6 | **Safety limit: 50 iterations** | Loop terminates to prevent runaway tokens |
| 7 | **Auto-discover models** | Refresh list with `council-orchestrator models` |
| 8 | **Follow Ponytail rules** | YAGNI → stdlib → native → one line → minimum. Mark simplifications with `ponytail:` comments |

## Activation

```bash
# Step 0 — Discover models (run once per session)
council-orchestrator models

# Step 1 — Initialize
council-orchestrator init "<full objective>"

# Step 2 — Enter loop
council-orchestrator status
```

The council reads `COUNCIL_MODELS.md`, picks the best model per role from what's actually connected, and executes each stage with its embedded pattern. The loop turns until done.
