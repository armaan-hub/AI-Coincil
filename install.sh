#!/bin/bash
# AI Council Skills Installer
# Run this anytime skills go missing: bash install.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
COPILOT_DIR="$HOME/.copilot/installed-plugins/superpowers-marketplace/superpowers/skills"
CLAUDE_DIR="$HOME/.claude/skills"
BIN_DIR="$HOME/bin"

skills=("council-orchestration" "ai-council-orchestration")

echo "🔵 Installing AI Council skills..."

for skill in "${skills[@]}"; do
  if [ -d "$COPILOT_DIR" ]; then
    mkdir -p "$COPILOT_DIR/$skill"
    cp "$SCRIPT_DIR/skills/$skill/SKILL.md" "$COPILOT_DIR/$skill/SKILL.md"
    echo "  ✅ Copilot CLI: $skill"
  fi

  if [ -d "$CLAUDE_DIR" ]; then
    mkdir -p "$CLAUDE_DIR/$skill"
    cp "$SCRIPT_DIR/skills/$skill/SKILL.md" "$CLAUDE_DIR/$skill/SKILL.md"
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
  cp "$SCRIPT_DIR/orchestrator.py" "$BIN_DIR/council-orchestrator"
  chmod +x "$BIN_DIR/council-orchestrator"
  echo "  ✅ PATH: council-orchestrator command"
fi

echo ""
echo "✅ Done! Skills installed: council-orchestration, ai-council-orchestration"
echo "   CLI command available: council-orchestrator"
echo ""
echo "   Invoke: /council-orchestration  or  /ai-council-orchestration"
echo "   Or:     council-orchestrator init \"<objective>\""
