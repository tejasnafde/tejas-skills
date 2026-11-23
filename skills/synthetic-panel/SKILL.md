---
name: synthetic-panel
description: >-
  Rank 5 to 10 ideas (feature ideas, onboarding copy, app store headlines,
  screenshot captions) with a cheap synthetic customer panel: LLM personas write
  free-text reactions, and Semantic Similarity Rating turns each reaction into a
  1 to 5 score. A pre-filter that picks which ideas go to a real test; not a
  forecast of installs, conversion or sales. Use for "which of these headlines",
  "rank these ideas", "test this copy on users", "synthetic panel".
user-invocable: true
argument-hint: "[items file or a list of ideas] [app or audience]"
---

# Synthetic panel

Rank a short list of ideas against one another before you spend a real test on
them. Personas from the app's real audience each react to one item in their own
words. Each reaction is scored by how close it is to anchor statements for the
scores 1 to 5 (SSR, [method](references/method.md)). Items are ranked by their mean
score, with an interval.

What it can do: separate clearly weak items from clearly strong ones, and choose
2 or 3 items for a live test. What it cannot do: predict installs, conversion,
revenue or retention, or replace talking to users.

## 1. Collect the items

- 2 to 15 items of the same kind (5 to 10 is best). Do not mix headlines with
  feature ideas in one run.
- One `context` line that says where the person sees the item, for example "You
  see this app in the app store, with this headline:".
- **Two controls:** one item that is clearly good and one that is clearly bad (spam,
  buzzwords, broken). If the panel cannot rank these correctly, the run is invalid.
- Format: [`examples/items.example.json`](examples/items.example.json). Put the files
  in the app's repo (for example `research/panel/`), not in this skill.

## 2. Build the personas

Read [personas](references/personas.md). In short: 30 to 50 personas whose mix
of country, city, age, income, phone and habits follows the app's real users,
from its analytics, not from guesses. Set `audience` and `calibrated` honestly.

## 3. Choose the question

`--question` picks the prompt and the anchor sets in `scripts/anchors.json`:

| Question | Use for |
|---|---|
| `download` (default) | Store headlines, short descriptions, screenshots |
| `appeal` | Feature ideas, onboarding promises |
| `clarity` | Onboarding copy, empty states, paywall text |

All anchor sets are ours and unvalidated (the paper's sets are not public).

## 4. Run

```sh
uv run -q --with google-genai python <skill>/scripts/panel.py run \
  --items research/panel/items.json --personas research/panel/personas.json \
  --out research/panel/runs/<date>-<topic> --question download \
  --project <gcp project> --log research/panel/calibration.jsonl
```

- Defaults: writer `gemini-3.5-flash-lite`, embedder `gemini-embedding-001`,
  temperature 0.5, every persona sees every item once. `--dry-run` prints the call
  count without credentials.
- Credentials: a Vertex AI key for a personal project (`roles/aiplatform.user`),
  through `GOOGLE_APPLICATION_CREDENTIALS`. On Tejas's Mac, read the "Google Cloud"
  section of `~/Desktop/projects/INFRA.md` first: the default ADC is a work identity.
- Cost: about 400 short calls for 10 items and 40 personas, a few cents.
  Runtime is under a minute.
- `--writer gemini-3.5-flash` gave a slightly larger good-to-bad gap in the
  pilot, at about 5 times the time. Do not use `gemini-embedding-2`: it scored
  worse in the pilot.
- Exit code 2 means the controls failed. Do not report the ranking; fix the
  items or the personas and run again.

## 5. Report

Show `summary.md` and add three short reactions per item from `reactions.jsonl`,
chosen to show the range (a high, a middle and a low score). Always:

- Report ranks. Say that items with overlapping intervals are a tie.
- Keep the label "Not yet calibrated for <audience>" while `calibrated` is false,
  and say that the anchor set is unvalidated.
- Never call the output user research, customer feedback or a survey of users.
- Recommend which 2 or 3 items go to a live test (store listing experiment,
  product page optimisation, an A/B test, or real users), not a final choice.
- Point out reactions that show a real objection (price, storage, privacy,
  language). Those are often worth more than the scores.

## 6. Calibrate

Every run with `--log` adds one line to the app's `calibration.jsonl`, with
`"outcome": null`. When a live result arrives (an experiment winner, conversion
per variant, or real users' ratings), fill `outcome` on that line. See
[method](references/method.md), "Calibration", for when an audience or an anchor
set may be marked calibrated.
