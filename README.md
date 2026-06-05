# tejas-skills

Personal skill library for AI coding agents. One format, works everywhere.

## Skills

| Skill | Invoke | Description |
|-------|--------|-------------|
| [dr-debug](./skills/dr-debug/SKILL.md) | `/dr-debug` | Hypothesis-driven root cause analysis — read → theorize → targeted greps → triage → loop |

## Install

```bash
git clone https://github.com/tejasnafde/tejas-skills
cd tejas-skills
chmod +x install.sh
./install.sh
```

The install script symlinks each skill into every agent tool detected on your machine:

| Target | Covers |
|--------|--------|
| `~/.agents/skills/` | All Claude Code profiles (`~/.claude`, `~/.claude-tech-team`, `~/.claude-tejas`, `~/.claude-ai-team`) + Codex |
| `~/.cursor/skills-cursor/` | Cursor |
| `~/.opencode/skills/` | OpenCode (when installed) |

Since these are **symlinks**, any edits you make to skill files in this repo are live immediately — no reinstall needed.

### Dry run

```bash
./install.sh --dry-run
```

## Adding a skill

```bash
mkdir skills/my-skill
cat > skills/my-skill/SKILL.md << 'EOF'
---
name: my-skill
description: >-
  One-line description of what this skill does.
user-invocable: true
argument-hint: "[optional args]"
---

# My Skill

Skill content here...
EOF

./install.sh   # picks up the new skill automatically
```

Then commit and push.

## Skill format

Skills use a single `SKILL.md` file with YAML frontmatter:

```markdown
---
name: skill-name           # kebab-case, matches directory name
description: >-            # shown in skill picker
  Short description.
user-invocable: true       # /skill-name works
argument-hint: "[args]"    # shown as usage hint
---

# Skill Title

Markdown instructions for the agent...
```

This format is understood natively by Claude Code (all profiles) and Codex.
Cursor reads the same file from `skills-cursor/`.
