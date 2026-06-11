#!/usr/bin/env python3
"""
Council Orchestrator — Autonomous Multi-Agent Loop Engine

The persistent state machine behind the AI Council pattern.
Inspired by Karpathy's autoresearch loop: keeps iterating through
Boot → Think → Plan → Create → Review → Verify until the objective is met.

Phase 0 (Boot): Scans the project, infers domain, generates domain-aware expert
agent personas in COUNCIL_AGENTS.md. All subsequent stages use these personas.

Usage (as invoked by the AI during orchestration):
    python orchestrator.py init "<objective>"          # Start a new council session (begins at "boot")
    python orchestrator.py status                      # Current stage & iteration
    python orchestrator.py advance <stage> <outcome>   # Mark stage complete
    python orchestrator.py loopback <stage> <reason>   # Go back to a stage
    python orchestrator.py check <output_path>         # Check if output satisfies objective
    python orchestrator.py models                      # Fetch live model catalog from proxy
    python orchestrator.py agents                      # Show current COUNCIL_AGENTS.md summary
"""

import json
import os
import sys
import subprocess
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

JOURNAL_FILE = "council_journal.md"
AGENTS_FILE = "COUNCIL_AGENTS.md"
MAX_ITERATIONS = 50  # safety limit to prevent infinite loops
MAX_LOOPS_PER_STAGE = 10

STAGE_ORDER = ["boot", "think", "plan", "create", "review", "verify"]


# ─── Data Model ──────────────────────────────────────────────────────────────

STATE_TEMPLATE = """
# Council Journal

## Objective
{objective}

## Metadata
- Started: {started}
- Iteration: 1
- Stage: think
- Loops: 0
- Total loops: 0

## Completion Criteria
{criteria}

## Stage History

### Iteration 1 — think

*No stages completed yet.*

## Decisions Log

*No decisions yet.*

## Deadman Switch
Last progress: {started}
"""


def init_journal(objective: str) -> dict:
    """Create a new council journal with the given objective."""
    now = _now()
    criteria = _generate_criteria(objective)

    state = {
        "objective": objective,
        "started": now,
        "iteration": 1,
        "stage": "boot",
        "loops": 0,
        "total_loops": 0,
        "max_iterations": MAX_ITERATIONS,
        "completed_stages": [],
        "history": [],
        "decisions": [],
        "deadman": now,
        "criteria": criteria,
        "domain": "",
        "agents_generated": False,
    }
    _write_state(state)
    print(f"✅ Council initialized | Iteration 1 | Stage: boot")
    print(f"   Objective: {objective[:80]}...")
    print(f"   Next: Run Phase 0 — scan project, detect domain, generate COUNCIL_AGENTS.md")
    print(f"   Max iterations: {MAX_ITERATIONS} (safety limit)")
    print(f"   Journal: {JOURNAL_FILE}")
    return state


def _generate_criteria(objective: str) -> list:
    """Generate a checklist of completion criteria from the objective."""
    criteria = [
        "All code compiles and runs without errors",
        "All tests pass",
        "The output solves the stated problem completely",
        "No known bugs or unresolved issues remain",
        "The solution is documented and explainable",
    ]
    # Add objective-specific criteria
    if any(kw in objective.lower() for kw in ["code", "implement", "build", "create", "write"]):
        criteria.insert(0, "Implementation is complete and functional")
    if any(kw in objective.lower() for kw in ["test", "verify", "check", "review"]):
        criteria.insert(0, "All verification criteria are satisfied")
    if any(kw in objective.lower() for kw in ["bug", "fix", "error", "issue"]):
        criteria.insert(0, "All identified bugs are fixed")
    return criteria


def get_state() -> dict:
    """Read the current council state from the journal."""
    if not os.path.exists(JOURNAL_FILE):
        return None

    with open(JOURNAL_FILE, "r") as f:
        content = f.read()

    # Parse the markdown journal
    state = _parse_journal(content)
    return state


def advance_stage(stage: str, outcome: str, notes: str = "") -> dict:
    """Advance the council to the next stage or next iteration."""
    state = get_state()
    if not state:
        print("❌ No council journal found. Run 'init' first.")
        sys.exit(1)

    stage = stage.lower()

    if stage not in STAGE_ORDER:
        print(f"❌ Unknown stage: {stage}. Valid: {', '.join(STAGE_ORDER)}")
        sys.exit(1)

    # Record this stage completion
    entry = {
        "iteration": state["iteration"],
        "stage": stage,
        "outcome": outcome,
        "notes": notes,
        "timestamp": _now(),
    }
    state.setdefault("history", []).append(entry)
    state["completed_stages"].append(stage)
    state["deadman"] = _now()
    state["loops"] = 0  # reset per-stage loop counter

    # Track agent generation
    if stage == "boot":
        state["agents_generated"] = True
        if os.path.exists(AGENTS_FILE):
            print(f"✅ COUNCIL_AGENTS.md found — domain-aware team assembled")

    # Determine next stage
    current_idx = STAGE_ORDER.index(stage)
    if current_idx < len(STAGE_ORDER) - 1:
        next_stage = STAGE_ORDER[current_idx + 1]
        state["stage"] = next_stage
        print(f"✅ Stage '{stage}' complete → advancing to '{next_stage}'")
        if next_stage == "think" and state.get("agents_generated"):
            print(f"   Agent team ready — personas from COUNCIL_AGENTS.md will be used")
    else:
        # Stage 5 (verify) complete — check if we need another iteration
        print(f"✅ Stage '{stage}' complete — iteration {state['iteration']} complete")
        state["stage"] = "__delivery_check__"

    _write_state(state)
    return state


def loopback(target_stage: str, reason: str) -> dict:
    """Loop back to a previous stage (or the same one) with context."""
    state = get_state()
    if not state:
        print("❌ No council journal found. Run 'init' first.")
        sys.exit(1)

    target_stage = target_stage.lower()

    if target_stage not in STAGE_ORDER:
        print(f"❌ Unknown stage: {target_stage}. Valid: {', '.join(STAGE_ORDER)}")
        sys.exit(1)

    # Increment loop counters
    state["loops"] = state.get("loops", 0) + 1
    state["total_loops"] = state.get("total_loops", 0) + 1

    # Check deadlock
    if state["loops"] > MAX_LOOPS_PER_STAGE:
        print(f"⚠️  DEADLOCK WARNING: {state['loops']} loops at stage '{target_stage}'")
        print(f"   Max per-stage: {MAX_LOOPS_PER_STAGE}")
        print(f"   Consider: different approach, more radical change, or escalate")

    if state["total_loops"] > state.get("max_iterations", MAX_ITERATIONS):
        print(f"❌ MAX ITERATIONS REACHED ({state.get('max_iterations', MAX_ITERATIONS)})")
        print(f"   Safety limit hit. Manual intervention required.")
        print(f"   Journal preserved at {JOURNAL_FILE} for review.")
        state["stage"] = "__maxed_out__"
        _write_state(state)
        return state

    # Record the loopback in history
    entry = {
        "iteration": state["iteration"],
        "stage": target_stage,
        "action": "loopback",
        "reason": reason,
        "loop_count": state["loops"],
        "timestamp": _now(),
    }
    state.setdefault("history", []).append(entry)
    state["stage"] = target_stage
    # Remove stages after target from completed list
    target_idx = STAGE_ORDER.index(target_stage)
    state["completed_stages"] = [
        s for s in state.get("completed_stages", [])
        if STAGE_ORDER.index(s) < target_idx
    ]
    state["deadman"] = _now()

    _write_state(state)
    print(f"🔄 Looping back to '{target_stage}' | Reason: {reason}")
    print(f"   Loop #{state['loops']} at this stage | Total loops: {state['total_loops']}")
    return state


def next_iteration() -> dict:
    """Advance to the next full iteration (stage 1 again)."""
    state = get_state()
    if not state:
        print("❌ No council journal found. Run 'init' first.")
        sys.exit(1)

    state["iteration"] += 1
    state["stage"] = "think"  # boot only runs once; agents persist in COUNCIL_AGENTS.md
    state["completed_stages"] = []
    state["loops"] = 0
    state["deadman"] = _now()

    # Record iteration transition
    entry = {
        "iteration": state["iteration"],
        "stage": "__new_iteration__",
        "action": "new_iteration",
        "reason": "Previous iteration complete, objective not yet satisfied",
        "timestamp": _now(),
    }
    state.setdefault("history", []).append(entry)

    _write_state(state)
    agents_note = " | COUNCIL_AGENTS.md retained" if state.get("agents_generated") else ""
    print(f"🔄 Starting Iteration {state['iteration']} | Stage: think{agents_note}")
    print(f"   Total loops so far: {state['total_loops']}")
    return state


def check_completion(output_path: str = None) -> dict:
    """Check if the objective has been satisfied based on criteria."""
    state = get_state()
    if not state:
        print("❌ No council journal found.")
        return {"complete": False, "reason": "No journal"}

    # Build a completion report
    report = {
        "complete": False,
        "iteration": state["iteration"],
        "total_loops": state.get("total_loops", 0),
        "completed_stages": state.get("completed_stages", []),
        "criteria": state.get("criteria", []),
        "satisfied_criteria": [],
        "unsatisfied_criteria": list(state.get("criteria", [])),
        "output_path": output_path,
    }

    # If we've made it through all 5 stages in this iteration, that's progress
    if len(state.get("completed_stages", [])) >= 5:
        report["complete"] = True  # will be confirmed by Verification agent
        report["reason"] = "All 5 stages completed in current iteration"

    _write_state(state)
    return report


def status() -> dict:
    """Print current council status."""
    state = get_state()
    if not state:
        print("❌ No council journal found. Run:")
        print(f"   python orchestrator.py init \"<your objective>\"")
        return None

    stage_icons = {
        "boot": "🚀", "think": "💭", "plan": "📋", "create": "🔧",
        "review": "🔍", "verify": "✅", "__delivery_check__": "📦",
        "__maxed_out__": "⚠️"
    }
    icon = stage_icons.get(state.get("stage", ""), "❓")

    agents_status = "✅ COUNCIL_AGENTS.md ready" if (state.get("agents_generated") and os.path.exists(AGENTS_FILE)) else "⏳ Boot pending — run Phase 0 first"

    print(f"\n{'='*60}")
    print(f"  COUNCIL STATUS")
    print(f"{'='*60}")
    print(f"  {icon} Stage:        {state.get('stage', 'unknown')}")
    print(f"  🔄 Iteration:    {state.get('iteration', 0)}")
    print(f"  🔁 Total loops:  {state.get('total_loops', 0)}")
    print(f"  ✅ Completed:    {', '.join(state.get('completed_stages', [])) or 'none'}")
    print(f"  📋 Criteria:     {len(state.get('criteria', []))} total")
    print(f"  🤖 Agent team:   {agents_status}")
    if state.get("domain"):
        print(f"  🌐 Domain:       {state.get('domain')}")
    print(f"  🎯 Objective:    {state.get('objective', 'N/A')[:60]}...")
    print(f"  🕐 Started:      {state.get('started', 'N/A')}")
    print(f"  🕐 Last activity: {state.get('deadman', 'N/A')}")
    print(f"{'='*60}\n")
    return state


PROXY_URL = "http://127.0.0.1:4001"
MODELS_CACHE = "council_models.md"


def fetch_models() -> dict:
    """Fetch live model list from the AI proxy and write COUNCIL_MODELS.md."""
    result = {"providers": {}, "all": []}
    try:
        req = urllib.request.Request(f"{PROXY_URL}/v1/models", method="GET")
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode())
    except Exception as e:
        print(f"⚠️  Proxy not reachable at {PROXY_URL}/v1/models: {e}")
        print("   Using embedded model catalog from SKILL.md instead.")
        return result

    raw = data.get("data", [])
    provider_order = [
        ("copilot", "GitHub Copilot", [
            ("claude-opus-4.6-1m", "Vision", "15x premium — strongest reasoning"),
            ("claude-sonnet-4.6", "Vision", "Balanced, great for planning/review"),
            ("claude-sonnet-4.5", "Vision", "Good all-rounder"),
            ("claude-haiku-4.5", "Vision", "0.33x — cheap, fast, good verifier"),
            ("gpt-5.4", "Vision", "Strong coder (OpenAI)"),
            ("gpt-5.2", "Vision", "Good coder (OpenAI)"),
            ("gpt-5-mini", "Vision", "FREE — versatile, good for verifier/critic"),
            ("grok-code-fast-1", "", "Fast coding assistant (xAI)"),
        ]),
        ("opencode", "OpenCode Zen (free tiers)", [
            ("minimax-m3", "", "Latest MiniMax — strong all-rounder"),
            ("minimax-m2.7", "", "1M context — best for large codebases"),
            ("minimax-m2.5", "", "1M context"),
            ("kimi-k2.6", "", "Strong reasoning (Moonshot AI)"),
            ("kimi-k2.5", "", "Strong reasoning (Moonshot AI)"),
            ("glm-5.1", "", "Latest GLM (Zhipu AI)"),
            ("glm-5", "", "GLM (Zhipu AI)"),
            ("deepseek-v4-pro", "", "DeepSeek Pro — strong reasoning"),
            ("deepseek-v4-flash", "", "DeepSeek Flash — fast generation"),
            ("qwen3.7-max", "", "Latest Qwen max — strongest Alibaba model"),
            ("qwen3.7-plus", "", "Qwen 3.7 plus"),
            ("qwen3.6-plus", "", "Qwen 3.6 plus — balanced"),
            ("qwen3.5-plus", "", "Qwen 3.5 plus"),
            ("mimo-v2-pro", "", "Mimo v2 Pro"),
            ("mimo-v2-omni", "", "Mimo v2 Omni"),
            ("mimo-v2.5-pro", "", "262K context — Mimo v2.5 Pro"),
            ("mimo-v2.5", "", "Mimo v2.5 — 262K context"),
            ("hy3-preview", "", "Hyperbolic YI-3 preview"),
            ("big-pickle", "", ""),
        ]),
        ("opencode-free", "OpenCode Zen (FREE)", [
            ("deepseek-v4-flash-free", "", "FREE — fast, good for verifier"),
            ("mimo-v2.5-free", "", "FREE"),
            ("minimax-m3-free", "", "FREE"),
            ("nemotron-3-super-free", "", "FREE"),

        ]),
        ("nvidia", "Nvidia NIM", [
            ("meta/llama-3.3-70b-instruct", "", "Llama 3.3 70B"),
            ("meta/llama-3.1-8b-instruct", "", "Llama 3.1 8B (fast, small)"),
            ("nvidia/llama-3.1-nemotron-70b-instruct", "", "Nemotron 70B"),
            ("nvidia/nemotron-3-ultra-550b-a55b", "", "Nemotron 3 Ultra"),
            ("mistralai/mistral-7b-instruct-v0.3", "", "Mistral 7B (fast, small)"),
        ]),
        ("ollama", "Ollama (local)", [
            ("qwen3:8b", "", "Qwen 3 8B (local)"),
            ("qwen3:14b", "", "Qwen 3 14B (local)"),
            ("llama3.3:70b", "", "Llama 3.3 70B (local)"),
        ]),
        ("groq", "Groq (if connected)", [
            ("llama-3.3-70b-versatile", "", "Llama 3.3 70B via Groq"),
            ("llama-3.1-8b-instant", "", "Llama 3.1 8B via Groq (fast)"),
            ("deepseek-r1-distill-llama-70b", "", "DeepSeek R1 via Groq"),
            ("mixtral-8x7b", "", "Mixtral MoE via Groq"),
            ("gemma2-9b-it", "", "Google Gemma 2 via Groq"),
        ]),
        ("gemini", "Google Gemini (if connected)", [
            ("gemini-2.5-pro", "", "Google Gemini 2.5 Pro"),
            ("gemini-2.5-flash", "", "Google Gemini 2.5 Flash"),
            ("gemini-2.0-flash", "", "Google Gemini 2.0 Flash"),
            ("gemini-1.5-pro", "", "Google Gemini 1.5 Pro"),
            ("gemini-1.5-flash", "", "Google Gemini 1.5 Flash"),
        ]),
        ("openai", "OpenAI (if connected)", [
            ("gpt-4o", "", "OpenAI GPT-4o"),
            ("gpt-4o-mini", "", "OpenAI GPT-4o mini"),
            ("o3-mini", "", "OpenAI o3-mini"),
            ("o4-mini", "", "OpenAI o4-mini"),
            ("gpt-4.1", "", "OpenAI GPT-4.1"),
            ("codex-mini-latest", "", "OpenAI Codex mini"),
        ]),
        ("openrouter", "OpenRouter (if connected)", [
            ("google/gemma-3-27b-it:free", "", "FREE — Gemma 3 via OpenRouter"),
            ("meta-llama/llama-3.3-70b-instruct:free", "", "FREE — Llama 3.3 via OpenRouter"),
            ("deepseek/deepseek-r1:free", "", "FREE — DeepSeek R1 via OpenRouter"),
            ("qwen/qwen3-8b:free", "", "FREE — Qwen 3 8B via OpenRouter"),
        ]),
        ("anthropic", "Claude (Anthropic, official)", [
            ("claude-sonnet-4-6", "", "Latest Sonnet"),
            ("claude-sonnet-4-5", "", "Sonnet 4.5"),
            ("claude-haiku-4-5", "", "Fast Haiku"),
            ("claude-opus-4-7", "", "Most capable Opus"),
            ("claude-opus-4-6", "", "Opus 4.6"),
            ("claude-opus-4-5", "", "Opus 4.5"),
        ]),
    ]

    # Build provider groups from live data
    live_groups = {}
    live_models = set()
    for m in raw:
        mid = m.get("id", "")
        if not mid:
            continue
        live_models.add(mid)
        # Normalize provider from owned_by to a consistent key
        owner_norm = (m.get("owned_by", "") or "").split("[")[0].strip().lower()
        if mid.startswith("copilot/") or "github-copilot" in owner_norm or "github" in owner_norm:
            live_groups.setdefault("github-copilot", []).append(mid)
        elif mid.startswith("opencode/"):
            live_groups.setdefault("opencode", []).append(mid)
        elif "ollama" in owner_norm or mid.startswith("qwen3:") or mid.startswith("llama3.3:"):
            live_groups.setdefault("ollama", []).append(mid)
        elif "nvidia" in owner_norm or mid.startswith("meta/") or mid.startswith("nvidia/") or mid.startswith("mistralai/"):
            live_groups.setdefault("nvidia", []).append(mid)
        elif "gemini" in owner_norm:
            live_groups.setdefault("gemini", []).append(mid)
        elif "openai" in owner_norm:
            live_groups.setdefault("openai", []).append(mid)
        elif "groq" in owner_norm:
            live_groups.setdefault("groq", []).append(mid)
        elif "openrouter" in owner_norm:
            live_groups.setdefault("openrouter", []).append(mid)
        else:
            live_groups.setdefault("opencode", []).append(mid)

    # Mark which providers are alive
    alive_providers = set()
    for grp, mids in live_groups.items():
        if mids:
            alive_providers.add(grp)

    # Also check which additional providers might be set up via config
    alive_providers.add("opencode-free")  # always available
    alive_providers.add("groq")
    alive_providers.add("gemini")
    alive_providers.add("openai")
    alive_providers.add("openrouter")
    alive_providers.add("anthropic")  # official claude

    # Store live groups for show_models to use
    result["live_groups"] = live_groups

    # Write the models catalog file
    lines = [
        "# Council Model Catalog",
        "",
        f"*Auto-generated: {_now()}*",
        f"*Proxy: {PROXY_URL}*",
        "",
        "## Available Models by Provider",
        "",
        "| Council Role | Recommended Model(s) | Why |",
        "|---|---|---|",
        "| **Thinker** | copilot/claude-opus-4.6-1m, opencode/qwen3.7-max, opencode/deepseek-v4-pro, opencode/kimi-k2.6 | Deep reasoning, strong analytical capability",
        "| **Planner** | copilot/claude-sonnet-4.6, opencode/qwen3.6-plus, opencode/minimax-m2.7 | Task decomposition, file mapping",
        "| **Creator** | copilot/gpt-5.4, opencode/deepseek-v4-flash, opencode/minimax-m2.7, copilot/grok-code-fast-1 | Code generation, TDD implementation",
        "| **Critic** | copilot/claude-sonnet-4.6, opencode/deepseek-v4-pro, opencode/kimi-k2.6 | Adversarial review, edge case analysis",
        "| **Reviewer** | copilot/claude-sonnet-4.6, opencode/qwen3.6-plus, opencode/minimax-m2.5 | Code quality, completeness check",
        "| **Verifier** | copilot/claude-haiku-4.5, copilot/gpt-5-mini, opencode/deepseek-v4-flash-free | Fast verification, cheap, good enough",
        "",
        "### Full Model Catalog",
        "",
    ]

    for key, label, model_list in provider_order:
        tag = " ✅" if key in alive_providers else " 🔌 (needs connect)"
        lines.append(f"### {label}{tag}")
        lines.append("")
        lines.append("| Model ID | Notes |")
        lines.append("|---|---|")
        for mid, extra, note in model_list:
            full_id = f"copilot/{mid}" if key == "copilot" and "/" not in mid else mid
            if key == "opencode":
                full_id = f"opencode/{mid}"
            elif key == "opencode-free":
                full_id = f"opencode/{mid}"
                mid_label = f"opencode/{mid}"
                lines.append(f"| {mid_label} | {note} |")
                continue
            elif key == "nvidia" and "/" in mid:
                full_id = mid
                mid_label = mid
                lines.append(f"| {mid_label} | {note} |")
                continue
            elif key in ("anthropic", "groq", "openai"):
                full_id = f"{key}/{mid}" if key != "openai" else mid
                lines.append(f"| {full_id} | {note} |")
                continue
            mid_label = full_id
            live = " ⚡" if full_id in live_models else ""
            lines.append(f"| {mid_label} | {note}{live} |")
        lines.append("")

    lines.extend([
        "",
        "---",
        "",
        "## Live Model Discovery",
        "",
        "To refresh this catalog with live data from the proxy:",
        "```bash",
        "council-orchestrator models",
        "```",
        "",
        "## Role-to-Model Mapping Strategy",
        "",
        "At council init, pick the best AVAILABLE model per role:",
        "",
        "1. Check which providers are connected (`/provider status`)",
        "2. For each role, pick the strongest model from a connected provider",
        "3. If GitHub Copilot is connected — use its Opus/Sonnet/Haiku for think/review/verify",
        "4. If only OpenCode — use deepseek-v4-pro for thinking, qwen3.7-max/plus for creation",
        "5. If budget conscious — use FREE models for verifier/critic roles",
        "6. Fallback: any connected model is better than no model",
        "",
    ])

    content = "\n".join(lines)
    try:
        with open(MODELS_CACHE, "w") as f:
            f.write(content)
        print(f"📋 Model catalog written to {MODELS_CACHE}")
    except Exception:
        pass

    result["all"] = raw
    # Build result providers from the normalized live_groups
    prov_label_map = {
        "github-copilot": "GitHub Copilot",
        "opencode": "OpenCode Zen",
        "nvidia": "Nvidia NIM",
        "ollama": "Ollama (local)",
        "gemini": "Google Gemini",
        "openai": "OpenAI",
        "groq": "Groq",
        "openrouter": "OpenRouter",
    }
    for grp, mids in live_groups.items():
        lbl = prov_label_map.get(grp, grp)
        result["providers"][lbl] = mids

    return result


def show_models() -> None:
    """Print live model list from proxy."""
    result = fetch_models()
    if not result["all"]:
        print("❌ No models fetched. Is the proxy running?")
        print(f"   Start: cd ~/Claude-Opencode-Ollama && node opencode-proxy-server.js &")
        return

    print(f"\n{'='*60}")
    print(f"  🤖 COUNCIL MODEL CATALOG")
    print(f"  {'='*60}")
    print(f"  Live models from proxy: {len(result['all'])}")
    print(f"  Providers: {len(result['providers'])}")
    print(f"{'='*60}")

    for label in ["GitHub Copilot", "OpenCode Zen", "Nvidia NIM", "Ollama (local)", "Google Gemini", "OpenAI", "Groq", "OpenRouter"]:
        models = result["providers"].get(label, [])
        if not models:
            continue
        print(f"\n  📦 {label} ({len(models)} models)")
        for m in sorted(models):
            print(f"     {m}")
    print(f"\n{'='*60}\n")
    print(f"💡 Role recommendations also written to {MODELS_CACHE}")


def show_agents() -> None:
    """Show a summary of the current COUNCIL_AGENTS.md agent team."""
    if not os.path.exists(AGENTS_FILE):
        print(f"❌ No {AGENTS_FILE} found.")
        print(f"   Run Phase 0 (boot) first: council-orchestrator status → stage 'boot'")
        print(f"   The boot phase scans the project, detects domain, and generates expert personas.")
        return

    with open(AGENTS_FILE, "r") as f:
        content = f.read()

    print(f"\n{'='*60}")
    print(f"  🤖 COUNCIL AGENT TEAM")
    print(f"{'='*60}")

    # Extract key info from COUNCIL_AGENTS.md
    lines = content.split("\n")
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## Project:") or stripped.startswith("## Domain:") or stripped.startswith("## Generated:"):
            print(f"  {stripped}")
        elif stripped.startswith("## ") and stripped not in ("## Project:", "## Domain:", "## Generated:"):
            print(f"\n  {stripped}")
        elif stripped.startswith("**Title:**"):
            title = stripped.replace("**Title:**", "").strip()
            print(f"    → {title}")

    print(f"\n{'='*60}")
    print(f"  📄 Full details: {AGENTS_FILE}")
    print(f"{'='*60}\n")


def compact() -> None:
    """Compact the journal by removing redundant entries."""
    state = get_state()
    if not state:
        print("❌ No council journal found.")
        return

    history = state.get("history", [])
    if len(history) > 100:
        # Summarize old history
        summary = {
            "action": "__compacted__",
            "previous_entries": len(history),
            "timestamp": _now(),
        }
        state["history"] = [summary] + history[-50:]
        print(f"📦 Journal compacted: {len(history)} → {len(state['history'])} entries")

    if state.get("agents_generated") and os.path.exists(AGENTS_FILE):
        print(f"✅ {AGENTS_FILE} preserved — agent personas intact after compaction")

    _write_state(state)


def snapshot() -> dict:
    """Print current state as JSON for machine parsing."""
    state = get_state()
    if not state:
        print(json.dumps({"error": "no_journal"}))
        return None
    # Remove large history for snapshot
    snapshot_state = {k: v for k, v in state.items() if k != "history"}
    print(json.dumps(snapshot_state, indent=2))
    return state


def history() -> None:
    """Print full iteration history."""
    state = get_state()
    if not state:
        print("❌ No council journal found.")
        return

    history = state.get("history", [])
    print(f"\n📜 COUNCIL HISTORY ({len(history)} entries)")
    print(f"{'='*60}")
    for i, entry in enumerate(history):
        if isinstance(entry, dict):
            ts = entry.get("timestamp", "?")[11:19]  # just HH:MM:SS
            stage = entry.get("stage", "?")
            action = entry.get("action", entry.get("outcome", "?"))
            notes = entry.get("notes", entry.get("reason", ""))
            print(f"  [{ts}] Iter {entry.get('iteration', '?')} | {stage:12s} | {action:20s} | {notes[:50]}")
        else:
            # Raw markdown table row from parsed journal
            print(f"  {entry}")
    print(f"{'='*60}\n")


# ─── Internal Helpers ────────────────────────────────────────────────────────


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _write_state(state: dict) -> None:
    """Serialize the state to the markdown journal file."""
    objective = state.get("objective", "N/A")
    started = state.get("started", _now())
    iteration = state.get("iteration", 1)
    stage = state.get("stage", "boot")
    loops = state.get("loops", 0)
    total_loops = state.get("total_loops", 0)
    deadman = state.get("deadman", _now())
    criteria = state.get("criteria", [])
    history_entries = state.get("history", [])
    decisions = state.get("decisions", [])
    completed = state.get("completed_stages", [])
    domain = state.get("domain", "")
    agents_generated = state.get("agents_generated", False)

    lines = [
        "# Council Journal",
        "",
        "## Objective",
        objective,
        "",
        "## Metadata",
        f"- Started: {started}",
        f"- Iteration: {iteration}",
        f"- Stage: {stage}",
        f"- Loops at stage: {loops}",
        f"- Total loops: {total_loops}",
        f"- Completed stages: {', '.join(completed) if completed else 'none'}",
        f"- Domain: {domain}",
        f"- Agents generated: {agents_generated}",
        "",
        "## Completion Criteria",
    ]
    for c in criteria:
        lines.append(f"- [ ] {c}")
    lines.extend([
        "",
        "## Stage History",
    ])

    if history_entries:
        for entry in history_entries:
            if isinstance(entry, dict):
                ts = entry.get("timestamp", "?")
                iter_n = entry.get("iteration", "?")
                stage_e = entry.get("stage", "?")
                action = entry.get("action", entry.get("outcome", "?"))
                notes = entry.get("notes", entry.get("reason", ""))
                lines.append(f"| {ts} | Iter {iter_n} | {stage_e} | {action} | {notes[:80]} |")
            elif isinstance(entry, str):
                # Entry is a raw markdown row from parsing — preserve as-is
                lines.append(entry)
    else:
        lines.append("*No stages completed yet.*")

    lines.extend([
        "",
        "## Decisions Log",
    ])
    if decisions:
        for d in decisions:
            lines.append(f"- {d}")
    else:
        lines.append("*No decisions yet.*")

    lines.extend([
        "",
        "## Deadman Switch",
        f"Last progress: {deadman}",
    ])

    content = "\n".join(lines) + "\n"
    with open(JOURNAL_FILE, "w") as f:
        f.write(content)


def _parse_journal(content: str) -> dict:
    """Parse the markdown journal back into a state dict."""
    state = {
        "objective": "",
        "started": "",
        "iteration": 1,
        "stage": "boot",
        "loops": 0,
        "total_loops": 0,
        "completed_stages": [],
        "history": [],
        "decisions": [],
        "deadman": "",
        "criteria": [],
        "domain": "",
        "agents_generated": False,
    }

    current_section = None
    for line in content.split("\n"):
        line_stripped = line.strip()

        if line_stripped.startswith("# ") and "Journal" in line_stripped:
            continue
        elif line_stripped == "## Objective":
            current_section = "objective"
        elif line_stripped == "## Metadata":
            current_section = "metadata"
        elif line_stripped == "## Completion Criteria":
            current_section = "criteria"
        elif line_stripped == "## Stage History":
            current_section = "history"
        elif line_stripped == "## Decisions Log":
            current_section = "decisions"
        elif line_stripped == "## Deadman Switch":
            current_section = "deadman"
        elif line_stripped.startswith("## "):
            current_section = None
        elif current_section == "objective" and line_stripped and not line_stripped.startswith("#"):
            if not state["objective"]:
                state["objective"] = line_stripped
        elif current_section == "metadata":
            if line_stripped.startswith("- Started:"):
                state["started"] = line_stripped.split(":", 1)[1].strip()
            elif line_stripped.startswith("- Iteration:"):
                state["iteration"] = int(line_stripped.split(":", 1)[1].strip())
            elif line_stripped.startswith("- Stage:"):
                state["stage"] = line_stripped.split(":", 1)[1].strip()
            elif line_stripped.startswith("- Loops at stage:"):
                state["loops"] = int(line_stripped.split(":", 1)[1].strip())
            elif line_stripped.startswith("- Total loops:"):
                state["total_loops"] = int(line_stripped.split(":", 1)[1].strip())
            elif line_stripped.startswith("- Completed stages:"):
                val = line_stripped.split(":", 1)[1].strip()
                state["completed_stages"] = [s.strip() for s in val.split(",") if s.strip() and s != "none"]
            elif line_stripped.startswith("- Domain:"):
                state["domain"] = line_stripped.split(":", 1)[1].strip()
            elif line_stripped.startswith("- Agents generated:"):
                val = line_stripped.split(":", 1)[1].strip().lower()
                state["agents_generated"] = val == "true"
        elif current_section == "criteria" and line_stripped.startswith("- ["):
            state["criteria"].append(line_stripped)
        elif current_section == "history" and line_stripped.startswith("|"):
            state["history"].append(line_stripped)
        elif current_section == "decisions" and line_stripped.startswith("- "):
            state["decisions"].append(line_stripped[2:])
        elif current_section == "deadman" and line_stripped.startswith("Last progress:"):
            state["deadman"] = line_stripped.split(":", 1)[1].strip()

    return state


# ─── CLI ─────────────────────────────────────────────────────────────────────


def main():
    if len(sys.argv) < 2:
        print("Usage: python orchestrator.py <command> [args...]")
        print("")
        print("Commands:")
        print("  init \"<objective>\"     Start a new council session (begins at 'boot')")
        print("  status                 Show current council state and agent team")
        print("  advance <stage> [notes] Mark stage complete, advance to next")
        print("  loopback <stage> <reason>  Loop back to a stage")
        print("  next-iteration         Start a new iteration (back to think)")
        print("  compact                Compact the journal")
        print("  snapshot               Print state as JSON")
        print("  history                Print iteration history")
        print("  check [path]           Check completion status")
        print("  models                 Fetch live model catalog from proxy")
        print("  agents                 Show current COUNCIL_AGENTS.md team summary")
        print("")
        print("Stages: boot → think → plan → create → review → verify")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "init":
        if len(sys.argv) < 3:
            print("Usage: python orchestrator.py init \"<objective>\"")
            sys.exit(1)
        init_journal(sys.argv[2])

    elif cmd == "status":
        status()

    elif cmd == "advance":
        if len(sys.argv) < 3:
            print("Usage: python orchestrator.py advance <stage> [notes]")
            sys.exit(1)
        stage = sys.argv[2]
        notes = sys.argv[3] if len(sys.argv) > 3 else ""
        advance_stage(stage, "passed", notes)

    elif cmd == "loopback":
        if len(sys.argv) < 4:
            print("Usage: python orchestrator.py loopback <stage> \"<reason>\"")
            sys.exit(1)
        loopback(sys.argv[2], sys.argv[3])

    elif cmd == "next-iteration":
        next_iteration()

    elif cmd == "compact":
        compact()

    elif cmd == "snapshot":
        snapshot()

    elif cmd == "history":
        history()

    elif cmd == "check":
        path = sys.argv[2] if len(sys.argv) > 2 else None
        result = check_completion(path)
        print(json.dumps(result, indent=2))

    elif cmd == "models":
        show_models()

    elif cmd == "agents":
        show_agents()

    else:
        print(f"❌ Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
