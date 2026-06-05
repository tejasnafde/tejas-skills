#!/usr/bin/env bash
# install.sh — wire tejas-skills into every agent tool on this machine
# Usage: ./install.sh [--dry-run]
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="$REPO_DIR/skills"
DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; RESET='\033[0m'
log()  { echo -e "${CYAN}[install]${RESET} $*"; }
ok()   { echo -e "${GREEN}  ✓${RESET} $*"; }
skip() { echo -e "${YELLOW}  ~${RESET} $*"; }

symlink() {
  local src="$1" dst="$2"
  if $DRY_RUN; then
    echo "  [dry-run] ln -sf $src → $dst"
    return
  fi
  mkdir -p "$(dirname "$dst")"
  if [[ -L "$dst" && "$(readlink "$dst")" == "$src" ]]; then
    skip "already linked: $dst"
  elif [[ -e "$dst" && ! -L "$dst" ]]; then
    echo "  ⚠ real file/dir exists at $dst — skipping (remove manually to replace)"
  else
    ln -sf "$src" "$dst"
    ok "linked: $(basename "$dst")"
  fi
}

# ── Discover skills in this repo ──────────────────────────────────────────────
skills=()
for d in "$SKILLS_DIR"/*/; do
  [[ -f "$d/SKILL.md" ]] && skills+=("$(basename "$d")")
done

if [[ ${#skills[@]} -eq 0 ]]; then
  echo "No skills found in $SKILLS_DIR"; exit 1
fi

echo ""
log "Found ${#skills[@]} skill(s): ${skills[*]}"
echo ""

# ── 1. ~/.agents/skills  (covers all Claude Code profiles + Codex) ─────────
log "Wiring into ~/.agents/skills (all Claude profiles + Codex)..."
for skill in "${skills[@]}"; do
  symlink "$SKILLS_DIR/$skill" "$HOME/.agents/skills/$skill"
done

# ── 2. ~/.cursor/skills-cursor  (Cursor) ─────────────────────────────────────
if [[ -d "$HOME/.cursor" ]]; then
  log "Wiring into ~/.cursor/skills-cursor (Cursor)..."
  for skill in "${skills[@]}"; do
    symlink "$SKILLS_DIR/$skill" "$HOME/.cursor/skills-cursor/$skill"
  done
else
  skip "~/.cursor not found — skipping Cursor"
fi

# ── 3. ~/.opencode/skills  (OpenCode) ────────────────────────────────────────
if [[ -d "$HOME/.opencode" ]]; then
  log "Wiring into ~/.opencode/skills (OpenCode)..."
  for skill in "${skills[@]}"; do
    symlink "$SKILLS_DIR/$skill" "$HOME/.opencode/skills/$skill"
  done
else
  skip "~/.opencode not found — skipping OpenCode"
fi

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
log "Done! Active skills:"
for skill in "${skills[@]}"; do
  echo "  • /$skill"
done
echo ""
if $DRY_RUN; then echo -e "${YELLOW}(dry-run: no changes made)${RESET}"; fi
