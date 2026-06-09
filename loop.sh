#!/bin/bash
# Loop — Pure Shell Recurrent Task Runner (Zero Dependencies)
#
# Fallback for environments without Python. Uses only bash + standard Unix tools.
#
# Usage:
#   ./loop.sh run "<command>" [--interval N] [--max-iterations N]
#   ./loop.sh status
#   ./loop.sh stop
#   ./loop.sh interactive "<command>"
#   ./loop.sh cron "<command>" --every "*/5 * * * *"
#
# Examples:
#   ./loop.sh run "python orchestrator.py status" --interval 30 --max-iterations 10
#   ./loop.sh interactive "python orchestrator.py advance think"
#   ./loop.sh cron "council-orchestrator status" --every "*/10 * * * *"

set -euo pipefail

LOOP_DIR="${LOOP_DIR:-$HOME/.loop}"
STATE_FILE="$LOOP_DIR/loop_state.sh"
MAX_ITERATIONS="${MAX_ITERATIONS:-9999}"

# ─── Helpers ─────────────────────────────────────────────────────────────────

_ensure_dir() {
  mkdir -p "$LOOP_DIR"
}

_timestamp() {
  date -u +"%Y-%m-%dT%H:%M:%SZ"
}

_save_state() {
  _ensure_dir
  cat > "$STATE_FILE" <<EOF
#!/bin/bash
# Loop State — auto-generated
LOOP_COMMAND="$LOOP_COMMAND"
LOOP_INTERVAL="$LOOP_INTERVAL"
LOOP_ITERATION="$LOOP_ITERATION"
LOOP_MAX_ITERATIONS="$LOOP_MAX_ITERATIONS"
LOOP_ACTIVE="$LOOP_ACTIVE"
LOOP_LAST_RUN="$LOOP_LAST_RUN"
LOOP_NEXT_RUN="$LOOP_NEXT_RUN"
LOOP_STARTED="$LOOP_STARTED"
LOOP_CONDITION="$LOOP_CONDITION"
EOF
  chmod +x "$STATE_FILE"
}

_load_state() {
  if [ -f "$STATE_FILE" ]; then
    source "$STATE_FILE"
  else
    LOOP_COMMAND=""
    LOOP_INTERVAL=0
    LOOP_ITERATION=0
    LOOP_MAX_ITERATIONS=$MAX_ITERATIONS
    LOOP_ACTIVE=true
    LOOP_LAST_RUN=""
    LOOP_NEXT_RUN=""
    LOOP_STARTED=""
    LOOP_CONDITION=""
  fi
}

# ─── Commands ────────────────────────────────────────────────────────────────

cmd_init() {
  local command="$1"
  local interval="${2:-0}"
  local max_iter="${3:-$MAX_ITERATIONS}"
  local condition="${4:-}"

  LOOP_COMMAND="$command"
  LOOP_INTERVAL="$interval"
  LOOP_ITERATION=0
  LOOP_MAX_ITERATIONS="$max_iter"
  LOOP_ACTIVE=true
  LOOP_LAST_RUN=""
  LOOP_NEXT_RUN=""
  LOOP_STARTED="$(_timestamp)"
  LOOP_CONDITION="$condition"

  _save_state

  local interval_str="self-paced"
  [ "$interval" -gt 0 ] && interval_str="every ${interval}s"

  echo ""
  echo "============================================================"
  echo "  🔁 LOOP INITIALIZED"
  echo "============================================================"
  echo "  ▶️  Command:     ${command:0:60}..."
  echo "  ⏱  Schedule:    $interval_str"
  echo "  🔁 Max iters:   $max_iter"
  if [ -n "$condition" ]; then
    echo "  🎯 Stop when:   $condition"
  fi
  echo "  📁 State:       $STATE_FILE"
  echo "============================================================"
  echo ""
  echo "  Next: ./loop.sh run   — execute one iteration"
  echo "        ./loop.sh status — check state"
  echo "        ./loop.sh stop   — halt the loop"
}

cmd_run() {
  _load_state

  if [ "$LOOP_ACTIVE" != "true" ]; then
    echo "⏸️  Loop is inactive. Run './loop.sh start' to reactivate."
    exit 0
  fi

  if [ "$LOOP_ITERATION" -ge "$LOOP_MAX_ITERATIONS" ]; then
    echo "⚠️  Max iterations reached ($LOOP_ITERATION)"
    LOOP_ACTIVE=false
    _save_state
    exit 0
  fi

  LOOP_ITERATION=$((LOOP_ITERATION + 1))
  local cmd="$LOOP_COMMAND"
  local interval="$LOOP_INTERVAL"
  local start_time end_time elapsed

  echo ""
  echo "============================================================"
  echo "  🔁 LOOP ITERATION $LOOP_ITERATION"
  echo "  Command: ${cmd:0:80}"
  if [ "$interval" -gt 0 ]; then
    echo "  Interval: ${interval}s"
  else
    echo "  Interval: self-paced"
  fi
  echo "============================================================"
  echo ""

  start_time=$(date +%s)

  # Execute the command
  set +e
  eval "$cmd"
  local exit_code=$?
  set -e

  end_time=$(date +%s)
  elapsed=$((end_time - start_time))

  LOOP_LAST_RUN="$(_timestamp)"

  if [ "$exit_code" -eq 0 ]; then
    echo ""
    echo "✅ Iteration $LOOP_ITERATION complete (${elapsed}s, exit=$exit_code)"
  else
    echo ""
    echo "❌ Iteration $LOOP_ITERATION failed (${elapsed}s, exit=$exit_code)"
  fi

  _save_state

  # If fixed interval, hint about next run
  if [ "$interval" -gt 0 ]; then
    echo "📡 Next run in ${interval}s..."
    echo "   Run: ./loop.sh run"
  fi
}

cmd_status() {
  _load_state

  if [ -z "$LOOP_STARTED" ]; then
    echo "❌ No loop state found. Run:"
    echo "   ./loop.sh run \"<command>\" [--interval N]"
    exit 1
  fi

  local icon="▶️  Running"
  [ "$LOOP_ACTIVE" != "true" ] && icon="⏹️  Stopped"

  local interval_str="self-paced"
  [ "$LOOP_INTERVAL" -gt 0 ] && interval_str="${LOOP_INTERVAL}s"

  local last_result="N/A"
  if [ -n "$LOOP_LAST_RUN" ]; then
    last_result="$LOOP_LAST_RUN"
  fi

  echo ""
  echo "============================================================"
  echo "  LOOP STATUS"
  echo "============================================================"
  echo "  $icon"
  echo "  🔁 Iteration:    $LOOP_ITERATION/$LOOP_MAX_ITERATIONS"
  echo "  ⏱  Interval:     $interval_str"
  echo "  🕐 Last run:     $last_result"
  echo "  ▶️  Command:      ${LOOP_COMMAND:0:60}"
  echo "  📁 State:        $STATE_FILE"
  echo "============================================================"
  echo ""
}

cmd_stop() {
  _load_state
  LOOP_ACTIVE=false
  _save_state
  echo "⏹️  Loop stopped after $LOOP_ITERATION iteration(s)"
}

cmd_start() {
  _load_state
  LOOP_ACTIVE=true
  _save_state
  echo "▶️  Loop reactivated (iteration $LOOP_ITERATION)"
}

cmd_interactive() {
  local command="$1"
  echo ""
  echo "🔄 Interactive loop mode"
  echo "   Command: $command"
  echo "   Press Enter to run each iteration. Ctrl+C to stop."
  echo ""

  local iter=0
  while true; do
    iter=$((iter + 1))
    echo ""
    echo "--- Iteration $iter ---"
    echo ""

    set +e
    eval "$command"
    set -e

    echo ""
    echo "--- Iteration $iter complete ---"
    echo "Press Enter to run again, Ctrl+C to stop."
    read -r
  done
}

cmd_cron() {
  local command="$1"
  local schedule="${2:-*/5 * * * *}"

  echo "📡 Creating cron entry for: $command"
  echo "   Schedule: $schedule"
  echo ""

  # Check if already installed
  if crontab -l 2>/dev/null | grep -q "$command"; then
    echo "⚠️  Cron entry already exists for this command."
    exit 0
  fi

  # Add to crontab
  (
    crontab -l 2>/dev/null || true
    echo "$schedule cd $(pwd) && $command >> $LOOP_DIR/cron.log 2>&1"
  ) | crontab -

  echo "✅ Cron entry added."
  echo "   Log: $LOOP_DIR/cron.log"
  echo ""
  echo "   To remove: crontab -e"
}

cmd_cleanup() {
  if [ -f "$STATE_FILE" ]; then
    rm -f "$STATE_FILE"
    echo "🧹 Loop state removed ($STATE_FILE)"
  else
    echo "📭 No loop state found."
  fi
}

cmd_help() {
  echo "Loop — Pure Shell Recurrent Task Runner"
  echo ""
  echo "Usage:"
  echo "  ./loop.sh run \"<command>\" [--interval N] [--max-iterations N]"
  echo "  ./loop.sh init \"<command>\" [--interval N] [--max-iterations N]"
  echo "  ./loop.sh status"
  echo "  ./loop.sh start"
  echo "  ./loop.sh stop"
  echo "  ./loop.sh interactive \"<command>\""
  echo "  ./loop.sh cron \"<command>\" --every \"*/5 * * * *\""
  echo "  ./loop.sh cleanup"
  echo ""
  echo "Examples:"
  echo "  ./loop.sh run \"python orchestrator.py status\" --interval 30"
  echo "  ./loop.sh interactive \"python orchestrator.py status\""
  echo "  ./loop.sh cron \"council-orchestrator status\" --every \"*/10 * * * *\""
}

# ─── Main ────────────────────────────────────────────────────────────────────

main() {
  local cmd="${1:-help}"

  case "$cmd" in
    init)
      shift
      local command="" interval=0 max_iter="$MAX_ITERATIONS" condition=""

      # Parse options
      while [ $# -gt 0 ]; do
        case "$1" in
          --interval) interval="$2"; shift 2 ;;
          --max-iterations) max_iter="$2"; shift 2 ;;
          --condition) condition="$2"; shift 2 ;;
          --self-paced) interval=0; shift ;;
          *)
            if [ -z "$command" ]; then
              command="$1"; shift
            else
              shift
            fi
            ;;
        esac
      done

      if [ -z "$command" ]; then
        echo "❌ No command specified."
        echo "Usage: ./loop.sh init \"<command>\" [--interval N]"
        exit 1
      fi

      cmd_init "$command" "$interval" "$max_iter" "$condition"
      ;;

    run)
      shift
      local command="" interval=0 max_iter="$MAX_ITERATIONS"

      # Parse options
      while [ $# -gt 0 ]; do
        case "$1" in
          --interval) interval="$2"; shift 2 ;;
          --max-iterations) max_iter="$2"; shift 2 ;;
          *)
            if [ -z "$command" ]; then
              command="$1"; shift
            else
              shift
            fi
            ;;
        esac
      done

      if [ -n "$command" ]; then
        # One-shot mode: run command with specified interval
        LOOP_COMMAND="$command"
        LOOP_INTERVAL="$interval"
        LOOP_ITERATION=0
        LOOP_MAX_ITERATIONS="$max_iter"
        LOOP_ACTIVE=true
        LOOP_STARTED="$(_timestamp)"
        LOOP_LAST_RUN=""
        LOOP_NEXT_RUN=""
        cmd_run
      else
        # Use stored state
        cmd_run
      fi
      ;;

    status) cmd_status ;;
    start) cmd_start ;;
    stop) cmd_stop ;;
    interactive)
      shift
      cmd_interactive "$*"
      ;;
    cron)
      shift
      local command="" schedule="*/5 * * * *"
      while [ $# -gt 0 ]; do
        case "$1" in
          --every) schedule="$2"; shift 2 ;;
          *)
            if [ -z "$command" ]; then
              command="$1"; shift
            else
              shift
            fi
            ;;
        esac
      done
      if [ -z "$command" ]; then
        echo "❌ No command specified."
        exit 1
      fi
      cmd_cron "$command" "$schedule"
      ;;
    cleanup) cmd_cleanup ;;
    help|--help|-h) cmd_help ;;
    *)
      echo "❌ Unknown command: $cmd"
      echo "Try: ./loop.sh help"
      exit 1
      ;;
  esac
}

main "$@"
