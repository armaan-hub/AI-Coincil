#!/usr/bin/env python3
"""
Loop Engine — Cross-Platform Recurrent Task Runner

A persistent state machine that tracks and schedules recurring task execution.
Works as the backend for the `/loop` pattern in any AI CLI environment.

Usage:
    loop init "command" --interval 30 --max-iterations 100
    loop status
    loop run
    loop schedule
    loop stop
    loop history
    loop cleanup
"""

import json
import os
import sys
import time
import subprocess
import platform
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

STATE_FILE = "loop_state.json"
DEFAULT_MAX_ITERATIONS = 9999
DEFAULT_INTERVAL = 0  # 0 = self-paced (model decides)


# ─── Data Model ──────────────────────────────────────────────────────────────

LOOP_STATE_TEMPLATE = {
    "command": "",
    "interval": DEFAULT_INTERVAL,       # seconds; 0 = self-paced
    "self_paced": True,                  # True if model decides timing
    "max_iterations": DEFAULT_MAX_ITERATIONS,
    "iteration": 0,
    "active": True,
    "condition": None,                   # Optional stop condition description
    "created_at": "",
    "last_run": None,
    "next_run": None,
    "history": [],
    "platform": platform.system().lower(),
}


def init_loop(command: str, interval: int = 0, max_iterations: int = DEFAULT_MAX_ITERATIONS,
              self_paced: bool = None, condition: str = None) -> dict:
    """Initialize a new loop with the given command."""
    if self_paced is None:
        self_paced = (interval == 0)

    state = dict(LOOP_STATE_TEMPLATE)
    state["command"] = command
    state["interval"] = interval
    state["self_paced"] = self_paced
    state["max_iterations"] = max_iterations
    state["condition"] = condition
    state["created_at"] = _now()
    state["iteration"] = 0
    state["active"] = True
    state["last_run"] = None
    state["next_run"] = None
    state["history"] = []
    state["platform"] = platform.system().lower()

    _write_state(state)
    _print_status(state)
    return state


def get_state() -> Optional[dict]:
    """Read the current loop state."""
    if not os.path.exists(STATE_FILE):
        return None
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"❌ Failed to read loop state: {e}")
        return None


def run_iteration() -> dict:
    """
    Execute one iteration of the loop command.
    Returns the updated state.
    """
    state = get_state()
    if not state:
        print("❌ No loop state found. Run 'loop init' first.")
        sys.exit(1)

    if not state.get("active", True):
        print("⏸️  Loop is inactive. Run 'loop start' to reactivate.")
        return state

    # Check max iterations
    if state["iteration"] >= state.get("max_iterations", DEFAULT_MAX_ITERATIONS):
        print(f"⚠️  Max iterations reached ({state['iteration']})")
        print("   Stopping loop. Increase --max-iterations to continue.")
        state["active"] = False
        _write_state(state)
        return state

    # Increment iteration
    state["iteration"] += 1
    current_iter = state["iteration"]
    cmd = state.get("command", "")
    interval = state.get("interval", 0)

    print(f"\n{'='*60}")
    print(f"  🔁 LOOP ITERATION {current_iter}")
    cmd_preview = cmd[:80] + "..." if len(cmd) > 80 else cmd
    print(f"  Command: {cmd_preview}")
    print(f"  Interval: {'self-paced' if interval == 0 else f'{interval}s'}")
    print(f"{'='*60}\n")

    # Execute the command
    start_time = time.time()
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=False,  # Let output pass through
            text=True,
        )
        exit_code = result.returncode
        success = (exit_code == 0)
    except Exception as e:
        print(f"❌ Command execution error: {e}")
        exit_code = -1
        success = False

    elapsed = time.time() - start_time
    now_ts = _now()

    # Record in history
    entry = {
        "iteration": current_iter,
        "timestamp": now_ts,
        "elapsed_seconds": round(elapsed, 2),
        "exit_code": exit_code,
        "success": success,
    }
    state.setdefault("history", []).append(entry)
    state["last_run"] = now_ts

    # Determine next run
    if interval > 0:
        state["next_run"] = now_ts  # actual scheduling is done externally
    else:
        state["next_run"] = None  # self-paced — model decides

    _write_state(state)

    outcome = "✅" if success else "❌"
    print(f"\n{outcome} Iteration {current_iter} complete ({elapsed:.1f}s, exit={exit_code})")

    return state


def schedule_next() -> dict:
    """
    Schedule the next run (platform-aware hint).
    Returns instructions for the AI model on how to proceed.
    """
    state = get_state()
    if not state:
        print("❌ No loop state found.")
        sys.exit(1)

    interval = state.get("interval", 0)
    iteration = state.get("iteration", 0)
    max_iter = state.get("max_iterations", DEFAULT_MAX_ITERATIONS)

    if iteration >= max_iter:
        print(f"⚠️  Max iterations reached ({iteration}/{max_iter})")
        print("   Loop is done. Run 'loop stop' to finalize.")
        return state

    if interval > 0:
        # Fixed interval — tell the model to use platform-specific scheduling
        print(f"\n📡 SCHEDULE NEXT: Run again in {interval}s")
        print(f"   Platform: {state.get('platform', 'unknown')}")
        print(f"   Iteration: {iteration}/{max_iter}")
        print()
        _print_platform_schedule_hint(state)
    else:
        # Self-paced — let the model decide
        print(f"\n📡 SCHEDULE NEXT: Self-paced")
        print(f"   Iteration: {iteration}/{max_iter}")
        print(f"   The model should decide when to run again based on context.")
        print()

    return state


def _print_platform_schedule_hint(state: dict) -> None:
    """Print platform-specific scheduling instructions for the AI model."""
    platform_name = state.get("platform", "")
    interval = state.get("interval", 0)
    cmd = state.get("command", "")

    if interval <= 0:
        return

    # Human-readable interval
    if interval < 60:
        interval_str = f"{interval}s"
    elif interval < 3600:
        interval_str = f"{interval // 60}m{interval % 60}s"
    else:
        interval_str = f"{interval // 3600}h{(interval % 3600) // 60}m"

    print("─── PLATFORM-SPECIFIC SCHEDULING ───")
    print()

    if "darwin" == platform_name or "linux" == platform_name:
        print(f"  Option A: loop status && loop run (check & execute)")
        print(f"  Option B: sleep {interval} && loop run (simple timer)")
        print(f"  Option C: ./loop.sh run \"{cmd}\" --interval {interval} (shell helper)")
        print()
    else:
        print(f"  Run 'loop run' every {interval_str}")
        print(f"  Or use the generic: ./loop.sh run \"{cmd}\" --interval {interval}")
        print()


def stop_loop() -> dict:
    """Stop the loop."""
    state = get_state()
    if not state:
        print("❌ No loop state found.")
        sys.exit(1)

    state["active"] = False
    state["next_run"] = None
    _write_state(state)

    total_iterations = state.get("iteration", 0)
    print(f"⏹️  Loop stopped after {total_iterations} iteration(s)")
    return state


def start_loop() -> dict:
    """Re-activate a stopped loop."""
    state = get_state()
    if not state:
        print("❌ No loop state found.")
        sys.exit(1)

    state["active"] = True
    _write_state(state)
    print(f"▶️  Loop reactivated (iteration {state.get('iteration', 0)})")
    return state


def show_status() -> Optional[dict]:
    """Print current loop status."""
    state = get_state()
    if not state:
        print("❌ No loop state found. Run:")
        print("   loop init \"<command>\" [--interval N]")
        return None

    interval = state.get("interval", 0)
    iteration = state.get("iteration", 0)
    max_iter = state.get("max_iterations", DEFAULT_MAX_ITERATIONS)
    active = state.get("active", True)
    history = state.get("history", [])
    self_paced = state.get("self_paced", interval == 0)

    interval_display = "self-paced" if self_paced else f"{interval}s"
    status_icon = "▶️  Running" if active else "⏹️  Stopped"
    last_run = state.get("last_run", "never")
    next_run = state.get("next_run", "model-decides" if self_paced else "pending")

    last_success = "N/A"
    if history:
        last_entry = history[-1]
        last_success = "✅" if last_entry.get("success") else "❌"

    print(f"\n{'='*60}")
    print(f"  LOOP STATUS")
    print(f"{'='*60}")
    print(f"  {status_icon}")
    print(f"  🔁 Iteration:    {iteration}/{max_iter}")
    print(f"  ⏱  Interval:     {interval_display}")
    print(f"  🕐 Last run:     {last_run}")
    print(f"  🕐 Last result:  {last_success}")
    print(f"  📋 History:      {len(history)} entries")
    print(f"  💻 Platform:     {state.get('platform', 'unknown')}")
    print(f"  ▶️  Command:      {state.get('command', 'N/A')[:60]}")
    if state.get("condition"):
        print(f"  🎯 Stop when:    {state['condition']}")
    print(f"{'='*60}\n")
    return state


def show_history() -> None:
    """Print full iteration history."""
    state = get_state()
    if not state:
        print("❌ No loop state found.")
        return

    history = state.get("history", [])
    print(f"\n📜 LOOP HISTORY ({len(history)} entries)")
    print(f"{'='*60}")
    if not history:
        print("  No iterations run yet.")
    else:
        for entry in history:
            iter_n = entry.get("iteration", "?")
            ts = entry.get("timestamp", "?")[11:19] if len(entry.get("timestamp", "")) > 11 else "?"
            elapsed = entry.get("elapsed_seconds", 0)
            success = entry.get("success", False)
            exit_code = entry.get("exit_code", -1)
            icon = "✅" if success else "❌"
            print(f"  {icon} Iter {iter_n:3d} | {ts} | {elapsed:6.1f}s | exit={exit_code}")
    print(f"{'='*60}\n")


def snapshot() -> None:
    """Print current state as JSON for machine parsing."""
    state = get_state()
    if not state:
        print(json.dumps({"error": "no_state"}))
        return
    # Omit full history for compact output
    snap = {k: v for k, v in state.items() if k != "history"}
    snap["history_count"] = len(state.get("history", []))
    print(json.dumps(snap, indent=2))


def cleanup() -> None:
    """Remove loop state file."""
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)
        print(f"🧹 Loop state removed ({STATE_FILE})")
    else:
        print(f"📭 No loop state to clean up ({STATE_FILE} not found)")


def detect_platform_mechanism() -> str:
    """
    Detect which platform recurrence mechanism is available.
    Returns: 'schedule_wakeup', 'cron_create', 'cron', 'sleep', 'interactive'
    """
    system = platform.system().lower()

    # Check for Claude Code tools by looking at environment hints
    if "CLAUDE_CODE" in os.environ or "CLAUDE" in os.environ:
        return "schedule_wakeup"  # Claude Code has built-in ScheduleWakeup

    if system == "darwin" or system == "linux":
        # Check if cron is available
        try:
            subprocess.run(["which", "crontab"], capture_output=True, check=True)
            return "cron"
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

    # Fallback: simple sleep loop
    return "sleep"


# ─── Internal Helpers ────────────────────────────────────────────────────────


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _write_state(state: dict) -> None:
    """Serialize state to JSON."""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def _print_status(state: dict) -> None:
    """Print a human-readable summary of the initial state."""
    interval = state.get("interval", 0)
    iteration = state.get("iteration", 0)
    max_iter = state.get("max_iterations", DEFAULT_MAX_ITERATIONS)
    cmd = state.get("command", "")
    self_paced = state.get("self_paced", interval == 0)

    interval_str = "self-paced" if self_paced else f"every {interval}s"

    print(f"\n{'='*60}")
    print(f"  🔁 LOOP INITIALIZED")
    print(f"{'='*60}")
    print(f"  ▶️  Command:    {cmd[:60]}{'...' if len(cmd) > 60 else ''}")
    print(f"  ⏱  Schedule:   {interval_str}")
    print(f"  🔁 Max iters:  {max_iter}")
    print(f"  💻 Platform:   {state.get('platform', 'unknown')}")
    if state.get("condition"):
        print(f"  🎯 Stop when:  {state['condition']}")
    print(f"  📁 State file: {STATE_FILE}")
    print(f"{'='*60}")
    print()
    print("  Next: loop run     — execute one iteration")
    print("        loop status   — check state")
    print("        loop schedule — print scheduling instructions")
    print("        loop stop     — halt the loop")


# ─── CLI ─────────────────────────────────────────────────────────────────────


def main():
    if len(sys.argv) < 2:
        print("Usage: loop <command> [args...]")
        print()
        print("Commands:")
        print("  init \"<command>\"           Start a new loop")
        print("    --interval N              Fixed interval in seconds (default: self-paced)")
        print("    --max-iterations N        Max iterations (default: 9999)")
        print("    --condition \"<desc>\"      Stop condition description")
        print("  status                     Show current loop state")
        print("  run                        Execute one iteration")
        print("  schedule                   Print scheduling instructions")
        print("  stop                       Halt the loop")
        print("  start                      Reactivate a stopped loop")
        print("  history                    Show iteration history")
        print("  snapshot                   Print state as JSON")
        print("  cleanup                    Remove loop state")
        print("  detect                     Detect available scheduling mechanism")
        print()
        print("Examples:")
        print("  loop init \"python orchestrator.py status\" --interval 300")
        print("  loop init \"council-orchestrator status\" --self-paced")
        print("  loop run && loop status")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "init":
        if len(sys.argv) < 3:
            print("Usage: loop init \"<command>\" [--interval N] [--max-iterations N] [--condition \"<desc>\"]")
            sys.exit(1)

        # Parse options
        command = sys.argv[2]
        interval = 0
        max_iterations = DEFAULT_MAX_ITERATIONS
        condition = None
        self_paced = None

        i = 3
        while i < len(sys.argv):
            if sys.argv[i] == "--interval" and i + 1 < len(sys.argv):
                interval = int(sys.argv[i + 1])
                i += 2
            elif sys.argv[i] == "--max-iterations" and i + 1 < len(sys.argv):
                max_iterations = int(sys.argv[i + 1])
                i += 2
            elif sys.argv[i] == "--condition" and i + 1 < len(sys.argv):
                condition = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--self-paced":
                self_paced = True
                interval = 0
                i += 1
            else:
                i += 1

        init_loop(command, interval, max_iterations, self_paced, condition)

    elif cmd == "status":
        show_status()

    elif cmd == "run":
        run_iteration()

    elif cmd == "schedule":
        schedule_next()

    elif cmd == "stop":
        stop_loop()

    elif cmd == "start":
        start_loop()

    elif cmd == "history":
        show_history()

    elif cmd == "snapshot":
        snapshot()

    elif cmd == "cleanup":
        cleanup()

    elif cmd == "detect":
        mechanism = detect_platform_mechanism()
        print(f"🔍 Detected scheduling mechanism: {mechanism}")
        print(f"   Platform: {platform.system().lower()}")

    else:
        print(f"❌ Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
