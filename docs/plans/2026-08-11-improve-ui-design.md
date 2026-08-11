# Improve UI Design

## Goal

Create an explicit-only `improve-ui` skill that acts as a UI magic wand. It discovers the UI-related skills available in the current environment, selects the smallest complementary set for the task, executes the improvement autonomously, verifies the result visually and technically, and iterates until the interface is materially better.

## Invocation

- Claude Code: `/improve-ui [target or goal]`
- Codex: `$improve-ui [target or goal]`
- With no arguments, inspect the current project and improve its highest-impact visible UI.
- Do not invoke implicitly.

## Architecture

The skill uses a hybrid discovery model:

1. A deterministic script scans repository, user, Codex-profile, and Claude-profile skill roots.
2. It resolves symlinks, deduplicates repeated installations, excludes `improve-ui`, and emits skill names, descriptions, and paths without loading full instructions.
3. The model classifies the UI task and semantically selects one lead skill plus at most three specialists.
4. The model reads each selected `SKILL.md` completely and sequences their workflows according to their responsibilities and gates.

This avoids a static registry, so future skills become available automatically while keeping discovery predictable and token-efficient.

## Selection Rules

- Prefer repository-scoped skills over user-scoped skills when they express project-specific conventions.
- Prefer narrow specialists over overlapping umbrella skills.
- Select one lead for implementation and only specialists that add a distinct capability.
- Cover design, implementation, motion, accessibility, copy, framework components, imagery, and visual review only when the task needs them.
- Never select `improve-ui` recursively.
- If selected skills conflict, explicit user instructions win; otherwise the narrower skill owns its specialty and the lead owns integration.

## Execution Flow

1. Resolve the target and inspect the project, working tree, stack, design system, and relevant UI.
2. Discover available skills and announce the chosen “wand stack” with a one-line rationale per skill.
3. Respect every selected skill's required gates, including design approval, test-first implementation, read-only boundaries, or prerequisites.
4. Inspect the current rendered UI before editing when browser or image tooling exists.
5. Implement the scoped improvement while preserving project conventions and unrelated changes.
6. Run relevant tests, linters, type checks, and builds.
7. Inspect responsive states, interaction states, accessibility, and visual quality.
8. Use an appropriate review specialist for a final audit and iterate on confirmed issues.
9. Report the improvement, selected skills, verification, and any remaining limitations.

## Safety and Fallbacks

- Treat explicit invocation as authorization for ordinary in-scope UI edits, not unrelated rewrites, dependency churn, destructive cleanup, or deployment.
- Preserve dirty-worktree changes and stop when overlapping user edits cannot be handled safely.
- Ask only for choices that materially change product direction or authorization.
- Do not install missing skills automatically. Continue with the best available set and report the omission.
- If visual tooling is unavailable, use static inspection and technical verification and disclose the limitation.
- If no frontend surface can be resolved, ask the user for a target rather than inventing one.

## Files

- `skills/improve-ui/SKILL.md`: concise orchestration workflow.
- `skills/improve-ui/scripts/discover_ui_skills.py`: deterministic metadata inventory.
- `skills/improve-ui/agents/openai.yaml`: UI metadata and explicit-only Codex policy.
- Tests for discovery, symlink deduplication, scope precedence, malformed metadata, and self-exclusion.
- `README.md`: skill catalog entry.

## Verification

- Run the discovery tests after first confirming they fail without the implementation.
- Run the skill-creator validator.
- Exercise discovery against isolated fixture roots and the real installed skill roots.
- Confirm `improve-ui` is excluded and future synthetic skills appear without registry changes.
- Run the repository installer in dry-run mode and verify the new skill is detected.
