# Method, evidence and limits

## Source

Maier et al., "LLMs Reproduce Human Purchase Intent via Semantic Similarity
Elicitation of Likert Ratings", arXiv 2510.08338 (PyMC Labs and Colgate-Palmolive,
October 2025). A preprint, not peer reviewed. Reference code:
[pymc-labs/semantic-similarity-rating](https://github.com/pymc-labs/semantic-similarity-rating)
(Apache-2.0).

## What the paper found

- Data: 57 personal care product concept surveys, 9,300 US respondents.
- Asking an LLM for a 1 to 5 number directly gives answers that cluster at 3 and
  almost never use 1 or 5.
- SSR (free text, then similarity to anchor statements) reached about 90% of
  human test-retest reliability for ranking concepts, with realistic score
  distributions (KS similarity above 0.85). Models: GPT-4o and Gemini 2.0 Flash,
  temperature 0.5. Embedder: OpenAI `text-embedding-3-small`. Six anchor sets.
- Demographics matter: without them the correlation fell from about 90% to 50%,
  and the scores were too high.
- Age and income patterns replicated well. Gender and region replicated less well.
- The models rate weak products lower than people do.

## How this skill scores

For each reaction and each anchor set:

1. gamma(k) = (1 + cos(reaction, anchor k)) / 2 for k = 1..5.
2. p(k) = (gamma(k) - min gamma) / sum over k of (gamma(k) - min gamma).
3. Average p over the anchor sets, then apply temperature scaling
   (p ** (1 / T), renormalised; T = 1 by default).
4. Score = sum of k * p(k). An item's score is the mean over its reactions,
   with a 90% percentile bootstrap interval.

This matches `similarities_to_pmf` and `ResponseRater` in the reference code
(checked by reading the source on 2026-11-23, with epsilon 0). Items whose
intervals overlap share a rank.

## How this skill differs from the paper

- **Models.** Gemini 2.0 Flash is retired. The writer is `gemini-3.5-flash-lite`
  and the embedder `gemini-embedding-001`, both on Vertex AI. The paper did not
  test them.
- **Anchors.** The paper's anchor sets are not public. Ours are in
  `scripts/anchors.json`, three sets per question, all unvalidated.
- **Questions.** The paper measured purchase intent. "Download", "appeal" and
  "clarity" are new questions.
- **Audience.** The paper used US respondents only. This skill builds personas
  from each app's real users, which can be any country.

## Pilot (2026-11-23)

8 personas (7 in Indian cities, 1 in the US), one good and one spam headline,
two repeats, two ad-hoc anchor sets. Results:

| Writer | Embedder | Good minus bad | Repeat r | Time for 32 calls |
|---|---|---|---|---|
| 3.1 Flash-Lite | 001 | 0.91 | 0.65 | 10 s |
| 3.5 Flash-Lite | 001 | 0.74 | 0.77 | 6 s |
| 3.5 Flash | 001 | 0.94 | 0.77 | 30 s |
| 4 Hydrogen | 001 | 0.78 | 0.93 | 79 s |
| 3.5 Flash-Lite | 2 | 0.48 | 0.57 | 6 s |

Every writer ranked the spam headline far below the good one. Hydrogen repeated
best but its personas sounded more alike, and it was much slower. This shows that
the pipeline works with these models; it does not show agreement with people.

Traps found: `gemini-3.5-flash` spends output tokens on thinking, so a low
`max_output_tokens` cuts replies in half (the script uses 2000).
`gemini-embedding-2` merges a list of inputs into one vector (the script sends one
text per call for it).

## Why the label "Not yet calibrated"

The method is measured against people only for US consumers and one product
category. Models know US, English-speaking consumers best, and a plausible
reaction from a persona in another country can be a stereotype. The label says
that nobody has measured the method for this audience yet. It is not a claim
that the result is wrong.

## Calibration

`calibration.jsonl` in the app's repo has one line per run. Fill `outcome` when a
live result exists, for example:

```json
"outcome": {"source": "Play store listing experiment", "date": "2026-12-20",
            "winner": "stop-planning", "ranking": ["stop-planning", "shared-list"]}
```

Set `calibrated: true` in a personas file only when at least three runs for that
audience have live outcomes, and the panel's top item was in the live top half
each time (or the Spearman correlation with a human rating study is at least
0.6). Record the evidence in the personas file's `source`. Mark an anchor set
`validated: true` only from the same kind of evidence, with a new anchors
`version`. If the panel disagrees with live results, say so in this file.

## Human comparison study (the real test)

1. 15 to 20 real users from the target audience rate the same 8 items, 1 to 5,
   with a short reason.
2. Split them into two random halves and correlate the halves' item means. This
   is the human ceiling.
3. Correlate the panel's item means with all humans' item means.
4. Agreement = panel correlation / human ceiling. The paper reached about 0.9.
   Below 0.5, do not use the panel for this audience.
