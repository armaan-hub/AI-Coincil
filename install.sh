#!/bin/bash
# AI Council Skills Installer
# Run this anytime skills go missing: bash install.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
COPILOT_DIR="$HOME/.copilot/installed-plugins/superpowers-marketplace/superpowers/skills"
CLAUDE_DIR="$HOME/.claude/skills"
BIN_DIR="$HOME/bin"

skills=("council-orchestration" "ai-council-orchestration" "loop" "ponytail" "ponytail-review" "ponytail-audit" "ponytail-debt" "ponytail-gain" "ponytail-help")

echo "🔵 Installing AI Council + Ponytail skills..."

for skill in "${skills[@]}"; do
  if [ -d "$COPILOT_DIR" ]; then
    mkdir -p "$COPILOT_DIR/$skill"
    cp "$SCRIPT_DIR/skills/$skill/SKILL.md" "$COPILOT_DIR/$skill/SKILL.md" 2>/dev/null || true
    echo "  ✅ Copilot CLI: $skill"
  fi

  if [ -d "$CLAUDE_DIR" ]; then
    mkdir -p "$CLAUDE_DIR/$skill"
    cp "$SCRIPT_DIR/skills/$skill/SKILL.md" "$CLAUDE_DIR/$skill/SKILL.md" 2>/dev/null || true
    echo "  ✅ Claude Code: $skill"
  fi
done

# Install orchestrator for council-orchestration
if [ -d "$CLAUDE_DIR/council-orchestration" ]; then
  cp "$SCRIPT_DIR/orchestrator.py" "$CLAUDE_DIR/council-orchestration/orchestrator.py"
  cp "$SCRIPT_DIR/program.md" "$CLAUDE_DIR/council-orchestration/program.md"
  echo "  ✅ Claude Code: orchestrator.py + program.md"
fi

# Install to PATH
if [ -d "$BIN_DIR" ]; then
  # Council orchestrator
  cp "$SCRIPT_DIR/orchestrator.py" "$BIN_DIR/council-orchestrator"
  chmod +x "$BIN_DIR/council-orchestrator"
  echo "  ✅ PATH: council-orchestrator command"

  # Loop engine (Python)
  cp "$SCRIPT_DIR/loop.py" "$BIN_DIR/loop"
  chmod +x "$BIN_DIR/loop"
  echo "  ✅ PATH: loop command (Python)"

  # Loop engine (Shell fallback)
  cp "$SCRIPT_DIR/loop.sh" "$BIN_DIR/loop.sh"
  chmod +x "$BIN_DIR/loop.sh"
  echo "  ✅ PATH: loop.sh command (shell fallback)"
fi

echo ""
echo "✅ Done! Skills installed: ${skills[*]}"
echo "   CLI commands:"
echo "     council-orchestrator  — council state management"
echo "     loop                  — cross-platform loop engine (Python)"
echo "     loop.sh               — loop engine (shell fallback)"
echo ""
echo "   Orchestration & Loop Invoke:"
echo "     /council-orchestration   | /ai-council-orchestration   | /loop"
echo "     council-orchestrator init | loop init                  | loop.sh run"
echo ""
echo "   Ponytail over-engineering prevention commands:"
echo "     /ponytail [lite|full|ultra|off] - Set the intensity, or turn it off"
echo "     /ponytail-review                - Review the current diff for over-engineering"
echo "     /ponytail-audit                 - Audit the whole repo for over-engineering"
echo "     /ponytail-debt                  - Harvest deferred ponytail: comments into a ledger"
echo "     /ponytail-gain                  - Show the measured impact scoreboard"
echo "     /ponytail-help                  - Quick reference for ponytail commands"
echo " "
