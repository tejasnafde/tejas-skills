---
name: unslop
description: >-
  Turns a UI that looks AI-generated or vibecoded into a designed interface with its own character. Use when the user says "unslop", says a screen "looks AI-generated", "looks vibecoded" or "looks like a template", or when a screen shows the usual tells: purple-to-blue gradients, glows, gradient text, emoji icons and labels, "New ✨" badges, glossy blobs, uppercase tracked labels, pulsing elements, or uneven spacing. Not for building new UI or general polish of an already designed screen; use frontend-design or improve-ui for those.
---

# Unslop

Adapted from [unslop](https://github.com/heydamir/unslop) by Damir Sokolovsky ([@heydamir](https://x.com/heydamir)), licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Changes: trimmed, the story-video feature removed, the description narrowed, and the style rules made into defaults. Keep this credit in copies.

Vibecoded UI fails in predictable ways. Every surface glows, every label has an emoji, the spacing is random, and the copy shouts. Unslopping fixes the craft and keeps the product: features, content, and section order stay, and every size, color, word, and image becomes deliberate.

Removing slop is half the job. A clean screen that could belong to any product is the next template. The difference between slop and craft is where the richness goes: slop spreads color and effects over the chrome, craft keeps the chrome quiet and puts the richness into one or two moments of content.

## Defaults, not laws

The values in [references/tokens.md](references/tokens.md) and the rules in the passes below are defaults. A real brand or the confirmed direction may override any of them, for example a brand that is bold, italic, or colorful. The signs in [references/signs.md](references/signs.md) may not be kept just because they are there; keep one only when the user says it is part of the brand.

## Run it

1. **Look at the screen.** Find the files that render it, then render it and take a screenshot so you judge what people see.
   - Only a live URL: `node <skill-dir>/scripts/snapshot.mjs <url> unslop/original.html [--dark|--light]`. It also saves `original.live.png`. Compare the two before you start, and work on a copy.
   - Only a screenshot: rebuild the screen as one static HTML file and treat it as the original.
2. **Audit.** Go through [references/signs.md](references/signs.md). List every sign, one line each, with where it lives.
3. **Decide how much to change.**
   - **Heavy slop:** run everything below.
   - **Light slop:** fix only what the audit found, take the direction from the existing brand, keep palette, type, layout, and visuals. Bigger ideas go in the report.
   - **No slop:** say so, suggest two or three refinements with exact values, and stop. Never change a good screen just to make it different.
4. **Set the direction and stop.** Write the five lines below. Show the audit and direction and wait for an answer, unless the user said to just do it.
5. **Fix in nine passes, in order,** each across the whole screen: spacing, color, icons, copy, type, layout, details, visuals, motion.
6. **Check.** Run the checklist, render again, and compare with the audit. Render at most three times per run.
7. **Report** the direction, a few lines per pass, any unverified claims, and any image prompt you wrote.

## Direction

Five short lines, derived from what the product does and who it is for, never from what is trending.

- **Product.** What it does and for whom, in one sentence.
- **Character.** Two or three concrete words, like `calm, exact, a little warm`. Not clean, modern, sleek, minimal, or premium.
- **World.** The place or material it belongs to: a note app near paper and ink, a monitoring tool near instruments and night shifts. The world tints the neutrals, the accent, and the visual.
- **Moments.** One or two places where the screen gets rich color and detail, chosen from what the product shows: a rendered object in the preview, a chart whose colors each mean a series.
- **Signature.** One small detail only this product would have, used consistently: a live status dot, keycaps, a route line.

A violet-to-blue gradient, sparkles, and glow are not brand even when they sit in the logo, unless the user says so.

## Passes

**1. Spacing.** A 4px grid, with 2px for nudges in small controls. Equal things get equal sizes. Space inside a group is smaller than space between groups. Icons, labels, and numbers each sit in one aligned column. Navigation rows 32 to 36 tall with 2 to 4 between them. Replace one-off values like `mt-[13px]`.

**2. Color.** One neutral ramp tinted toward the world for background, surfaces, borders, and text. App and dashboard surfaces stay near grey; landing pages may tint further. Three text roles. One accent in the chrome, used rarely, at 4.5:1 contrast with text on it. Moments may use rich color where each color means something. Semantic colors only carry meaning. Remove hue gradients on surfaces, gradient text, colored glows and shadows, color washes, blobs, and neon borders. Borders are hairlines at 6 to 10% of the text color.

**3. Icons.** Emoji used as icons or decoration become line icons from one set (the project's set, else lucide), one size and stroke, in the text role color. Drop icons that add nothing.

**4. Copy.** Headlines say what the product does for whom, from facts already on the page. No exclamation marks, greeting headlines, hype words, or `AI-powered` on everything. Short labels. A change says what it compares to: `+12% vs last month`. No trailing periods on short strings. Mock data is plausible. Ask about claims you cannot check and remove them unless confirmed.

**5. Type.** Choose for the character; keep a real brand font. One interface family plus at most one partner (a mono or a display face). Few sizes; hierarchy from size and color rather than heavy weights. Sentence case instead of uppercase tracked labels. No negative tracking on small text. `tabular-nums` and one number format.

**6. Layout.** Keep the sections and their order. Apps keep real proportions (sidebar 240 to 280, fluid content). A landing hero is a scene with the headline on its calm part, or an asymmetric split; stacked and centered only for a short hero with no visual. One primary and at most one secondary action. Quiet navigation. Compose the first screen with no dead band. On mobile, stack in reading order and simplify dense previews instead of zooming them.

**7. Details.** Nested radius: inner = outer minus padding, at least 4. Counts and meta become quiet text, shortcuts become keycaps. One main chart, clearly the biggest, with one accent and the rest in neutral steps; secondary data is a list or table. Stat cards are a label, a figure, and a change. Vary card widths. Visible hover and focus states inside the palette. The signature appears where it belongs and nowhere else.

**8. Visuals.** Decorative filler goes. Dashboards rarely need generated images; their moments come from the product. A landing hero shows something true: a scene from the world when an image tool exists, otherwise a coded preview of what the page promises. Read [references/visuals.md](references/visuals.md) before this pass; [references/effects.md](references/effects.md) has optional code treatments.

**9. Motion.** Remove looping motion on things that are not live, `transition-all`, bouncy springs, `hover:scale` on cards, and parallax. Keep motion that explains something. Name transitioned properties; never animate layout properties. One easing curve, few durations, at most one entrance on load.

## Do not

- Rename the product. Redraw a slop logo flat: the wordmark, or a simple one-color glyph.
- Change what the product is, or invent features, claims, or data.
- Replace removed decoration with new decoration, or swap one trend for another (glass, grain, neon, bento).
- Fall back to the same look for every product.

## Checklist

- [ ] The direction is written and every pass follows it
- [ ] Spacing on the 4px scale, equal things equal, columns aligned
- [ ] One tinted neutral ramp, three text roles, one accent with enough contrast
- [ ] No hue gradients, gradient text, glows, colored shadows, color blobs, or emoji
- [ ] One icon set at one size and stroke
- [ ] Type chosen for the character, sentence case, tabular numbers in one format
- [ ] No exclamation marks, greeting headline, or unverified claims
- [ ] Nested radii add up
- [ ] A hero has a real visual or a product preview with a moment, never filler
- [ ] No looping or bouncy motion, no animated layout properties
- [ ] Template check: with another product's name, would the screen still fit? If yes, push the direction harder
