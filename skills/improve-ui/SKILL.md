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

When there is no code for the target:

- **Only a live URL.** Save the page with `node "<skill-dir>/scripts/snapshot.mjs" <url> improve-ui/original.html`, adding `--dark` or `--light` to match the theme the user sees. It also writes `original.live.png`. Render the saved copy, compare it with the screenshot, and work on a copy. Script-drawn animated backgrounds do not survive, so describe them from the live page. It needs Playwright; if it is missing, tell the user the one install command.
- **Only a screenshot.** Rebuild the screen as one static HTML file that matches it closely, and treat that file as the original.
- In both cases the result is a redesigned page the user hands to whoever owns the real site. Say so in the report.

Classify the mode, since it sets what may change:

- **Create:** build the requested surface; inherit the surrounding system when one exists.
- **Redesign:** replace visual decisions while keeping required content and behavior.
- **Refine:** develop the existing intention and keep everything outside the request. Visual-only work keeps the wording fixed; copy-only work keeps the presentation fixed. Report problems outside the scope instead of fixing them.
- **Review:** report prioritized findings and change nothing. No source edits, formatting, dependency installs, or files in the project; keep screenshots and reports outside it. Skip steps 6 and 7, and give each finding a location, the observed issue, its effect on the user, and a fix. Do not invent findings to fill a report.

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
3. The direction from step 6, once the user has confirmed it.
4. A specialist within its narrow domain.
5. The lead for integration and everything outside specialist domains.

Announce the selection briefly:

```text
Wand stack
- Lead: <skill>: <why it owns this task>
- Specialist: <skill>: <distinct contribution>
```

Do not turn this announcement into a plan dump.

## 4. Establish the baseline

Before editing:

1. Read repository instructions and inspect the dirty worktree. Preserve unrelated and overlapping user changes.
2. Detect the framework, styling system, component library, design tokens, routes, tests, and run commands.
3. Inspect the current rendered UI with browser or image tooling when available. Capture the relevant viewport and interaction states.
4. Run the rendered check when the page is served (see below) and save its report as the baseline.
5. Audit against [references/slop-signs.md](references/slop-signs.md). List every sign you find, one line each, with where it lives.
6. Identify the few issues with the greatest effect on hierarchy, comprehension, usability, accessibility, and perceived quality.

Use the current interface as evidence. Do not redesign from a file list alone when a renderable surface exists.

The rendered check:

```bash
node "<skill-dir>/scripts/inspect.mjs" <url> --out=<dir outside the project> [--viewport=1440x900 --viewport=390x844] [--selector=<css>]
```

Run it from the project folder. It resolves `playwright` or `playwright-core` and `axe-core` from the project, and uses an installed Chrome, Chromium, or Brave (or `CHROME_PATH`). It checks contrast, button and link names, form labels, image alt text, sideways overflow, broken images, JavaScript errors, text under 12px, and repeated copy, and saves a full-page screenshot per viewport. Exit 0 means no confirmed errors, 1 means confirmed errors, 2 means incomplete coverage. Small text and repeated copy are signals to judge, not defects to drive to zero. If the dependencies are missing, do not install them without asking; state that the check did not run. Its runs do not count toward the render limit.

## 5. Decide how much to change

Read the audit honestly before planning anything:

- **Heavy.** Many problems across color, type, icons, layout, and copy. Run the full process.
- **Light.** A mostly designed screen with a few problems left. Fix only what the audit found. Take the direction from the existing brand instead of inventing one, and keep the palette, type, layout, and visuals. Bigger ideas go into the report as suggestions, not changes.
- **None.** Say so plainly. Suggest two or three refinements at most, with exact values. Apply them only if the user agrees, then stop.

Never change a good screen just to make it different.

## 6. Set the direction and stop

For heavy and light changes, write five short lines before any edit. Derive them from what the product does and who it is for, never from what is trending.

- **Product.** What it does and for whom, in one plain sentence.
- **Character.** Two or three concrete words, like `calm, exact, a little warm`. Clean, modern, sleek, minimal, and premium are not allowed: they describe every template.
- **World.** The place or material the product belongs to. A note app lives near paper and ink, a monitoring tool near instruments and night shifts. The world tints the neutrals, the accent, and any visual.
- **Moments.** One or two places where the screen gets rich color, material, and detail, chosen from what the product shows. The chrome around them stays quiet.
- **Signature.** One small detail only this product would have, used consistently. One detail, not five.

Keep a real brand (a logo, color, or typeface that is not generic AI styling) and build the direction around it.

Show the audit, the chosen level, and the direction to the user and wait for an answer, since changing the direction later means redoing the work. Skip the wait only when the user already said to just do it. Pass the confirmed direction to every selected skill as the shared brief, so specialists do not each apply their own taste.

## 7. Execute the improvement

Sequence the selected skills rather than blending their instructions indiscriminately:

1. Use discovery or review specialists to establish concrete findings.
2. Respect every selected skill's gates, including design approval, test-first work, prerequisites, read-only boundaries, and stop conditions.
3. Let the lead implement the coherent result using existing project conventions and tokens.
4. Use specialists for their owned details, then return integration control to the lead.

Fix in passes, in this order, finishing each pass across the whole screen before the next: spacing, color, icons, copy, type, layout, details, visuals, motion. Spacing comes first because everything reads differently once the rhythm is right. Copy comes before type and layout because the length of a headline decides its size and position. Visuals and motion come last because they must fit a screen that already works without them. When nearly every line changes, plan the passes in order and write the new screen in one go, as long as every pass is applied.

Content rules:

- Do not invent features, claims, or data. Placeholder content that means nothing may become plausible content that does.
- Claims you cannot check, like `Trusted by 10,000+ teams` or `10x faster`, stay only if the user confirms they are real. Ask, and list them in the report.
- Do not replace removed decoration with new decoration, or swap one trend for another.

Prefer a focused, complete improvement over touching every possible surface. Keep behavior intact unless changing it is necessary to satisfy the UI goal.

## 8. Verify and iterate

Run the project's relevant tests, type checks, linting, and build checks. Then inspect the result at the target viewport plus representative narrow and wide responsive states. Exercise important hover, focus, active, loading, empty, error, and reduced-motion states when they exist.

Render the screen at most three times per run, counting from the baseline capture. Batch fixes between renders instead of rendering after each one.

Check at minimum:

- Visual hierarchy and consistency
- Responsive layout and overflow
- Keyboard access, focus visibility, semantics, labels, and contrast
- Interaction feedback and motion behavior
- Console errors, broken assets, regressions, and test failures
- Every sign from the baseline audit is gone, or deliberately kept with a reason
- Template check: if you swapped in another product's name, would the screen still fit? If yes, push the direction harder in the copy, the visual, and the signature detail

Run the rendered check again with a fresh `--out` directory and compare it with the baseline.

Claim only what the evidence shows. Each kind of evidence supports different claims:

- **Source:** intended structure and behavior, copy, and icon use.
- **Rendered:** composition, type, crops, colors, overflow, and the states actually captured.
- **Interaction:** controls, keyboard paths, and state changes actually exercised.
- **Project checks:** the exact commands run and their results.

A passing build does not prove visual quality, a screenshot does not prove keyboard access, and passing a few axe rules is not WCAG conformance. Never present more checks, fewer effects, or a different style as proof of better design.

Use a selected review specialist for a final audit when one fits. Iterate on confirmed issues until the result is materially improved and verification is clean. Do not chase speculative polish after the important issues are resolved.

If visual tooling is unavailable, use static inspection and technical checks, state that limitation, and do not claim pixel-level verification.

## 9. Report the result

Lead with what improved. Include the mode, the level and direction, the wand stack used, files changed, the checks that actually ran with their results, the checks that did not run, any unverified claims you asked about, and any remaining limitation or user decision. Keep the handoff concise and do not make the user reconstruct the workflow from progress updates.
