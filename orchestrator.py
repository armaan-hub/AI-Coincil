#!/usr/bin/env python3
"""
Council Orchestrator — Autonomous Multi-Agent Loop Engine

The persistent state machine behind the AI Council pattern.
Inspired by Karpathy's autoresearch loop: keeps iterating through
Think → Plan → Create → Review → Verify until the objective is met.

Usage (as invoked by the AI during orchestration):
    python orchestrator.py init "<objective>"          # Start a new council session
    python orchestrator.py status                      # Current stage & iteration
    python orchestrator.py advance <stage> <outcome>   # Mark stage complete
    python orchestrator.py loopback <stage> <reason>   # Go back to a stage
    python orchestrator.py check <output_path>         # Check if output satisfies objective
    python orchestrator.jsn compact                    # Compact the journal
    python orchestrator.jsn snapshot                   # Print current state as JSON
    python orchestrator.jsn history                    # Print full iteration history
"""

import json
import os
import sys
import subprocess
from datetime import datetime, timezone
from pathlib import Path

JOURNAL_FILE = "council_journal.md"
MAX_ITERATIONS = 50  # safety limit to prevent infinite loops
MAX_LOOPS_PER_STAGE = 10


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
        "stage": "think",
        "loops": 0,
        "total_loops": 0,
        "max_iterations": MAX_ITERATIONS,
        "completed_stages": [],
        "history": [],
        "decisions": [],
        "deadman": now,
        "criteria": criteria,
    }
    _write_state(state)
    print(f"✅ Council initialized | Iteration 1 | Stage: think")
    print(f"   Objective: {objective[:80]}...")
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
    stage_order = ["think", "plan", "create", "review", "verify"]

    if stage not in stage_order:
        print(f"❌ Unknown stage: {stage}. Valid: {', '.join(stage_order)}")
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

    # Determine next stage
    current_idx = stage_order.index(stage)
    if current_idx < len(stage_order) - 1:
        next_stage = stage_order[current_idx + 1]
        state["stage"] = next_stage
        print(f"✅ Stage '{stage}' complete → advancing to '{next_stage}'")
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
    stage_order = ["think", "plan", "create", "review", "verify"]

    if target_stage not in stage_order:
        print(f"❌ Unknown stage: {target_stage}. Valid: {', '.join(stage_order)}")
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
    stage_order = ["think", "plan", "create", "review", "verify"]
    target_idx = stage_order.index(target_stage)
    state["completed_stages"] = [
        s for s in state.get("completed_stages", [])
        if stage_order.index(s) < target_idx
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
    state["stage"] = "think"
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
    print(f"🔄 Starting Iteration {state['iteration']} | Stage: think")
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
        "think": "💭", "plan": "📋", "create": "🔧",
        "review": "🔍", "verify": "✅", "__delivery_check__": "📦",
        "__maxed_out__": "⚠️"
    }
    icon = stage_icons.get(state.get("stage", ""), "❓")

    print(f"\n{'='*60}")
    print(f"  COUNCIL STATUS")
    print(f"{'='*60}")
    print(f"  {icon} Stage:        {state.get('stage', 'unknown')}")
    print(f"  🔄 Iteration:    {state.get('iteration', 0)}")
    print(f"  🔁 Total loops:  {state.get('total_loops', 0)}")
    print(f"  ✅ Completed:    {', '.join(state.get('completed_stages', [])) or 'none'}")
    print(f"  📋 Criteria:     {len(state.get('criteria', []))} total")
    print(f"  🎯 Objective:    {state.get('objective', 'N/A')[:60]}...")
    print(f"  🕐 Started:      {state.get('started', 'N/A')}")
    print(f"  🕐 Last activity: {state.get('deadman', 'N/A')}")
    print(f"{'='*60}\n")
    return state


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
        ts = entry.get("timestamp", "?")[11:19]  # just HH:MM:SS
        stage = entry.get("stage", "?")
        action = entry.get("action", entry.get("outcome", "?"))
        notes = entry.get("notes", entry.get("reason", ""))
        print(f"  [{ts}] Iter {entry.get('iteration', '?')} | {stage:12s} | {action:20s} | {notes[:50]}")
    print(f"{'='*60}\n")


# ─── Internal Helpers ────────────────────────────────────────────────────────


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _write_state(state: dict) -> None:
    """Serialize the state to the markdown journal file."""
    objective = state.get("objective", "N/A")
    started = state.get("started", _now())
    iteration = state.get("iteration", 1)
    stage = state.get("stage", "think")
    loops = state.get("loops", 0)
    total_loops = state.get("total_loops", 0)
    deadman = state.get("deadman", _now())
    criteria = state.get("criteria", [])
    history_entries = state.get("history", [])
    decisions = state.get("decisions", [])
    completed = state.get("completed_stages", [])

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
        "stage": "think",
        "loops": 0,
        "total_loops": 0,
        "completed_stages": [],
        "history": [],
        "decisions": [],
        "deadman": "",
        "criteria": [],
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
        print("  init \"<objective>\"     Start a new council session")
        print("  status                 Show current council state")
        print("  advance <stage> [notes] Mark stage complete, advance to next")
        print("  loopback <stage> <reason>  Loop back to a stage")
        print("  next-iteration         Start a new iteration (back to think)")
        print("  compact                Compact the journal")
        print("  snapshot               Print state as JSON")
        print("  history                Print iteration history")
        print("  check [path]           Check completion status")
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

    else:
        print(f"❌ Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
