---
name: improve-ui
description: >-
  Explicitly invoked UI magic-wand orchestrator that discovers available skills, selects a complementary stack, improves an existing interface end to end, verifies it visually and technically, and iterates on confirmed issues. Use only when explicitly invoked as /improve-ui or $improve-ui for UI redesigns, polish, accessibility, responsive behavior, motion, copy, component work, or broad "make this better" requests.
---

# Improve UI

Act as the integrator for the best UI skills currently available. Discover them at invocation time, choose the smallest complementary wand stack, and own the result from baseline inspection through verified improvement.

## 1. Resolve the target

Interpret the invocation arguments as a route, component, file, screenshot, URL, visual problem, or product goal.

With no arguments:

1. Inspect the current project and its recent or uncommitted work.
2. Identify the highest-impact visible UI that can be run and verified locally.
3. Continue autonomously when one target clearly dominates.
4. Ask one focused question when there are multiple materially different products or no frontend surface can be resolved.

Explicit invocation authorizes ordinary edits needed for the scoped UI improvement. It does not authorize deployment, destructive cleanup, unrelated refactors, broad dependency churn, or changes outside the user's target.

## 2. Discover available skills

Resolve this skill's directory from the loaded `SKILL.md`, then run:

```bash
python3 "<skill-dir>/scripts/discover_ui_skills.py" --format markdown
```

The inventory scans repository, user, Codex-profile, and Claude-profile skill roots. It deduplicates symlinked installations, prefers closer repository scopes when names collide, and excludes `improve-ui` itself.

Do not rely on a memorized list of skills. Re-run discovery on every invocation so future additions participate automatically. If the script cannot run, inspect the same roots manually and continue; do not install, update, or enable skills as a fallback.

## 3. Build the wand stack

Classify the target by the capabilities it genuinely needs: visual direction, implementation, framework components, motion, accessibility, copy, imagery, responsive behavior, or final review.

Choose:

- **One lead** that can own the implementation and integration.
- **At most three specialists**, each adding a distinct capability the lead does not cover deeply.

Favor the narrowest relevant specialist over an overlapping umbrella skill. Prefer repository-scoped guidance over generic user guidance. Mandatory workflow dependencies count toward the specialist limit. Skip candidates that are read-only when implementation is needed unless they have a clear baseline or final-audit role.

For every selected skill, read its `SKILL.md` completely before acting. Read only the supporting resources that its instructions require for this task. Never recursively select `improve-ui`.

Resolve instruction conflicts in this order:

1. Explicit user instructions.
2. Safety, authorization, and repository guidance.
3. A specialist within its narrow domain.
4. The lead for integration and everything outside specialist domains.

Announce the selection briefly:

```text
Wand stack
- Lead: <skill> — <why it owns this task>
- Specialist: <skill> — <distinct contribution>
```

Do not turn this announcement into a plan dump.

## 4. Establish the baseline

Before editing:

1. Read repository instructions and inspect the dirty worktree. Preserve unrelated and overlapping user changes.
2. Detect the framework, styling system, component library, design tokens, routes, tests, and run commands.
3. Inspect the current rendered UI with browser or image tooling when available. Capture the relevant viewport and interaction states.
4. Identify the few issues with the greatest effect on hierarchy, comprehension, usability, accessibility, and perceived quality.

Use the current interface as evidence. Do not redesign from a file list alone when a renderable surface exists.

## 5. Execute the improvement

Sequence the selected skills rather than blending their instructions indiscriminately:

1. Use discovery or review specialists to establish direction and concrete findings.
2. Respect every selected skill's gates, including design approval, test-first work, prerequisites, read-only boundaries, and stop conditions.
3. Let the lead implement the coherent result using existing project conventions and tokens.
4. Use specialists for their owned details, then return integration control to the lead.

Prefer a focused, complete improvement over touching every possible surface. Keep behavior intact unless changing it is necessary to satisfy the UI goal.

## 6. Verify and iterate

Run the project's relevant tests, type checks, linting, and build checks. Then inspect the result at the target viewport plus representative narrow and wide responsive states. Exercise important hover, focus, active, loading, empty, error, and reduced-motion states when they exist.

Check at minimum:

- Visual hierarchy and consistency
- Responsive layout and overflow
- Keyboard access, focus visibility, semantics, labels, and contrast
- Interaction feedback and motion behavior
- Console errors, broken assets, regressions, and test failures

Use a selected review specialist for a final audit when one fits. Iterate on confirmed issues until the result is materially improved and verification is clean. Do not chase speculative polish after the important issues are resolved.

If visual tooling is unavailable, use static inspection and technical checks, state that limitation, and do not claim pixel-level verification.

## 7. Report the result

Lead with what improved. Include the wand stack used, files changed, verification performed, and any remaining limitation or user decision. Keep the handoff concise and do not make the user reconstruct the workflow from progress updates.
