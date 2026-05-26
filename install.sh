#!/bin/bash
# AI Council Skills Installer
# Run this anytime skills go missing: bash install.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
COPILOT_DIR="$HOME/.copilot/installed-plugins/superpowers-marketplace/superpowers/skills"
CLAUDE_DIR="$HOME/.claude/skills"

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

echo ""
echo "✅ Done! Restart Copilot CLI / Claude Code to see the skills."
echo "   Use: /council-orchestration  or  /ai-council-orchestration"
