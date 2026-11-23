#!/usr/bin/env bash
# install.sh — wire tejas-skills into every agent tool on this machine
# Usage: ./install.sh [--dry-run]
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="$REPO_DIR/skills"
DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

# Links must point at the main checkout. From a git worktree they would point
# into a folder that is deleted when the worktree is removed.
if git -C "$REPO_DIR" rev-parse --git-dir >/dev/null 2>&1 &&
   [[ "$(git -C "$REPO_DIR" rev-parse --path-format=absolute --git-dir)" != \
      "$(git -C "$REPO_DIR" rev-parse --path-format=absolute --git-common-dir)" ]]; then
  echo "install.sh: $REPO_DIR is a git worktree. Run it from the main checkout." >&2
  exit 1
fi

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; RESET='\033[0m'
log()  { echo -e "${CYAN}[install]${RESET} $*"; }
ok()   { echo -e "${GREEN}  ✓${RESET} $*"; }
skip() { echo -e "${YELLOW}  ~${RESET} $*"; }

symlink() {
  local src="$1" dst="$2"
  if $DRY_RUN; then
    echo "  [dry-run] ln -sfn $src → $dst"
    return
  fi
  mkdir -p "$(dirname "$dst")"
  if [[ -L "$dst" && "$(readlink "$dst")" == "$src" ]]; then
    skip "already linked: $dst"
  elif [[ -e "$dst" && ! -L "$dst" ]]; then
    echo "  ⚠ real file/dir exists at $dst — skipping (remove manually to replace)"
  else
    ln -sfn "$src" "$dst"
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

# ── 1. ~/.agents/skills  (Codex, and the target of the profile links) ─────
log "Wiring into ~/.agents/skills (Codex)..."
for skill in "${skills[@]}"; do
  symlink "$SKILLS_DIR/$skill" "$HOME/.agents/skills/$skill"
done

# ── 1b. Claude Code profiles: ~/.claude/skills and ~/.claude-*/skills ───────
# Claude Code reads only <profile>/skills, so each skill needs a link in each
# profile: <profile>/skills/<skill> -> ../../.agents/skills/<skill>.
# A profile is wired only when it already links at least one skill from this
# repo. That keeps profiles that were left without these skills untouched.
# To opt a profile in, link one skill into it by hand and run this again.
uses_repo_skills() {
  local dir="$1" s target
  for s in "${skills[@]}"; do
    [[ -L "$dir/$s" ]] || continue
    target="$(readlink "$dir/$s")"
    case "$target" in
      ../../.agents/skills/"$s"|"$HOME/.agents/skills/$s"|"$SKILLS_DIR/$s") return 0 ;;
    esac
  done
  return 1
}

for profile in "$HOME/.claude" "$HOME"/.claude-*; do
  [[ -d "$profile/skills" ]] || continue
  name="$(basename "$profile")"
  if ! uses_repo_skills "$profile/skills"; then
    skip "$name: no skills from this repo linked yet, skipping"
    continue
  fi
  log "Wiring into ~/$name/skills (Claude Code profile)..."
  for skill in "${skills[@]}"; do
    symlink "../../.agents/skills/$skill" "$profile/skills/$skill"
  done
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
