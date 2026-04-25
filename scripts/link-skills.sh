#!/bin/bash
# Links skill files from repo into ~/.claude/skills/
# Run once after cloning, or after adding new skill files.

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_DIR="$HOME/.claude/skills"

mkdir -p "$SKILLS_DIR"

for skill_file in "$REPO_DIR/skills/"*.md; do
    filename="$(basename "$skill_file")"
    target="$SKILLS_DIR/$filename"
    if [ -L "$target" ]; then
        rm "$target"
    fi
    ln -s "$skill_file" "$target"
    echo "Linked: $target -> $skill_file"
done

echo "Skills linked to $SKILLS_DIR"
