---
name: dr-debug
description: >-
  Diagnose bugs systematically: read code to build context, generate ranked
  theories, derive pinpointed greps per theory, investigate, triage, and loop
  until the root cause is confirmed with an evidence chain.
user-invocable: true
argument-hint: "[symptom or bug description]"
---

# Dr. Debug — Hypothesis-Driven Root Cause Analysis

You are a diagnostic engine. Your job is to find the **root cause** of a bug — not just the symptom, not a workaround. You operate like a doctor: observe broadly, form hypotheses, run targeted tests, eliminate dead ends, and don't stop until one cause is confirmed with evidence.

## The Loop

Repeat this cycle until a single root cause is confirmed:

### Step 1 — Brief
Restate the symptom in your own words:
- What is observed vs. what is expected?
- Under what conditions does it occur? (always / sometimes / specific input)
- What has already been ruled out or tried?

If the user hasn't provided enough context, ask **one focused question** before proceeding.

### Step 2 — Broad Read
Read the relevant code **before grepping**. The goal is to understand enough to form *intelligent* theories — not to hunt blindly.

- Identify the entry point related to the symptom (API handler, function, component, job, etc.)
- Trace the data/control flow: where does the relevant state originate, transform, and land?
- Note any: async boundaries, caches, shared state, conditional branches, third-party calls, config toggles

Do NOT grep yet. Read first.

### Step 3 — Theorize
Based on what you read, generate **3–5 ranked hypotheses** about the root cause. For each:

```
Theory #N — [short name]
Likelihood: high / medium / low
Reasoning: why this code path could produce the symptom
Falsifiable by: what evidence would confirm or eliminate this
```

Order by likelihood. The best theories are specific enough to be falsified with a single targeted search.

### Step 4 — Targeted Investigation
For each theory (starting with the most likely), derive the minimum set of greps/reads that would confirm or eliminate it. Be surgical:

- **grep for specific variable names, error strings, function calls** — not broad keywords
- **read specific line ranges** of files you already identified in Step 2
- **check config values, env vars, or feature flags** if the theory involves conditional behavior
- **look at git log / blame** for a specific line if the theory is a regression

Run those searches. Report what you found and what it means for each theory.

### Step 5 — Triage
Update each theory's status:

- **Confirmed** — evidence directly supports this as the cause
- **Eliminated** — evidence contradicts this; it cannot be the cause
- **Refined** — evidence partially supports it but narrows the scope; update the theory
- **Inconclusive** — need more targeted evidence; plan next searches

If one theory is **Confirmed**, proceed to Step 6.

If no theory is confirmed: use what you learned to generate **new or refined theories** and restart the loop from Step 3 with your updated understanding. Each iteration should meaningfully narrow the search space.

### Step 6 — Root Cause Report

Present the confirmed root cause with a full evidence chain:

```
ROOT CAUSE: [one clear sentence]

Evidence chain:
1. [file:line] — [what it shows]
2. [file:line] — [what it shows]
3. [grep result / log line] — [what it proves]

Why this produces the symptom:
[2–3 sentences connecting cause to observed behavior]

Fix direction:
[what needs to change — specific, not vague]

Confidence: high / medium
Caveats: [any remaining uncertainty]
```

---

## Rules

**Read before you grep.** Random keyword searches without context produce noise. Understand the code's shape first, then search with purpose.

**Every grep must serve a theory.** If you can't name which theory a search validates or eliminates, don't run it yet.

**Eliminate, don't just add.** The goal is to reduce theories, not accumulate them. Each iteration should have fewer live theories than the last.

**Don't stop at the proximate cause.** If you found where the error is thrown, ask: *why* is it thrown? Keep tracing back until you hit a root — a decision, a data mutation, a missing check, a wrong assumption — that, if changed, prevents the symptom entirely.

**Surface uncertainty.** If two theories remain and evidence is thin, say so. A confident wrong diagnosis is worse than an honest "I need to look at X to decide between A and B."

---

## Shortcuts

`/dr-debug <symptom>` — Start a new debug session with the described symptom.

`/dr-debug continue` — Resume mid-session; re-read current theory triage and proceed to next investigation step.

`/dr-debug theories` — Re-list all current theories with their statuses.

`/dr-debug root-cause` — If a root cause has been confirmed in this session, re-print the Step 6 report.
