---
name: chat-keepsake
description: >-
  Turn a long chat export (WhatsApp, Telegram, iMessage) into a personal keepsake
  for someone: a scrollable single-page site built from their real messages, plus a
  printable handwritten letter. Use for birthdays, anniversaries, farewells, graduations,
  apologies, thank-yous, or "I want to make something for X out of our chat".
user-invocable: true
argument-hint: "[path to chat export] [who it is for] [occasion]"
---

# Chat Keepsake

You are building someone a gift out of their own words. The raw material is a chat
export, often five to ten years of it. The output is a single-page site they open on
their phone, and optionally a printed letter.

This works because it is **evidence**. Every quote is real, every date is real. The
moment you invent something the whole thing collapses into a greetings card. Guard that.

---

## Hard rules

Break these and the gift fails, no matter how good the prose is.

1. **Verify every quote against the raw export before it ships.** Sub-agents paraphrase
   and reorder without meaning to. Run `scripts/verify_quotes.py`. Zero misses, always.
2. **Never invent the sender's interior life.** Not their feelings, not their motives, not
   what they "could not let go of". If a line asserts an emotion the chat does not contain,
   flag it and get explicit sign-off.
3. **Get copy approved before deploying.** Show the paragraph, wait, then build. The person
   commissioning this knows things the archive does not.
4. **The commissioner is not the author of the archive.** Do not write "I read all ten years
   of our messages" when an agent did the reading. Find a true framing.
5. **Ask what is off-limits before you write anything.** Old fights, exes, mental health,
   things the recipient does not know. Assume nothing is fair game.
6. **Statistics are not feelings.** See "Numbers" below.
7. **Strip EXIF from every photo** before it goes on a public URL.

---

## Phase 0 — Scope it

Ask, in one message, and wait:

- Who is it for, what is the relationship, and what is the occasion?
- What is off-limits? Name the categories explicitly: fights, exes, family, health,
  anything the recipient does not already know about the commissioner.
- How is it delivered? Private link, file, printed, all three?
- Is there anything they already know is the emotional centre? Often they do.

Then read the chat yourself before proposing a shape. Do not pitch a structure from the
occasion alone.

---

## Phase 1 — Parse and measure

```bash
python3 scripts/parse_chat.py "<export.txt>" --out work/
```

This produces `work/stats.json`, `work/parsed.jsonl`, and era chunk files in
`work/chunks/`. It handles both WhatsApp date formats and stitches continuation lines.

Read `stats.json` and look for **narrative** facts, not trivia:

- **Long silences.** These are almost always the story. A 512-day gap is a chapter.
- **The busiest single day and month.** Something happened. Go and find out what.
- **The longest unbroken streak.** The peak of the friendship, datable.
- **Who sends more, and who speaks first after each silence.** This is usually the most
  moving fact in the entire archive and it is invisible without computing it.
- **Where the volume collapses**, and whether it recovers.

---

## Phase 2 — Deep read, in parallel

Chunk by era, then spawn one agent per chunk. Six chunks of roughly equal message count
works well for a decade.

Each agent gets the same brief:

- Read the ENTIRE chunk with repeated Read calls. No skimming, no sampling.
- Preserve the language exactly. Hinglish, Marathi, typos, keysmashes, all of it. Never
  translate or clean up.
- Return: era summary, 30 to 50 verbatim quotes with exact dates and speaker, running
  jokes with first and last use, turning points, what this era shows about the recipient
  as a person with evidence, and every birthday or occasion exchange.
- Prefer short exchanges of two to four messages over long monologues.
- State plainly that the report is data, not prose for a human.

Give each agent the era's known peculiarity ("this year has 43 messages, find out why").
They come back with far better material when they are hunting something specific.

---

## Phase 3 — Verify, then verify the verification

Sub-agent reports are leads, not sources. Before any quote enters a draft, grep it out of
the raw export yourself and read the surrounding twenty lines. In practice roughly one in
ten quotes comes back with the message order wrong, the speaker wrong, or two exchanges
merged.

Once the page exists:

```bash
python3 scripts/verify_quotes.py site/index.html "<export.txt>"
```

It pulls every message bubble and pull-quote out of the HTML and checks each against the
export. Do not deploy with misses.

---

## Phase 4 — Find the spine

A keepsake needs one thread, not a list of highlights. Look for:

- **A phrase that survives the whole archive.** The first real message and the most recent
  message being the same joke is worth more than any statistic.
- **A reversal.** Something the commissioner did for the recipient years ago that the
  recipient did back, or vice versa. Ritual is the strongest structure available.
- **A promise never kept**, small and specific. It gives the ending something to ask for.
- **A prediction that came true**, especially one the recipient made and the commissioner
  did not believe at the time.
- **What the recipient does that they get no credit for.** Usually practical and
  unglamorous. Find three instances across different years and it becomes a theme.

Tell the commissioner the spine you found before writing to it. They will confirm or
correct it in one line, and it saves a rewrite.

---

## Phase 5 — Draft

### Numbers

Keep numbers that carry story. Cut everything else.

Keep: total messages, days elapsed versus days actually talking, silence lengths, the
per-year decline, one absurd single-day count.

Cut: percentages, emoji frequency counts, average message length, "you used X 115 times".
Nobody has ever felt anything about a percentage. A specific 3am message beats every
aggregate in the archive.

One restrained per-year bar chart is usually the only chart worth having.

### Voice

- Short sentences. Plain words. One idea per sentence.
- Let the messages carry the emotion. Your prose sets up and gets out of the way. If a
  paragraph explains why a quote is moving, cut the paragraph.
- Never explain a joke. Quote the recipient's caption verbatim and stop.
- Write the commissioner as slightly worse than the recipient, if the archive supports it.
  It reads as honest instead of self-congratulatory.
- Do not write about the difficult parts of the commissioner's past in detail. Two
  sentences, self-aware, then move on. "I will spare you the full inventory. You were
  there for most of it" does more than a confession.
- Prefer things the commissioner actually typed at the time over your summary of how they
  felt. Search for their real reaction. It is nearly always better.

### Structure that works

Opening sequence, then chapters in chronological order, ending in the present tense.

1. A short self-playing sequence: the first exchange appearing message by message, a
   number counting up, a title. This is the "video" without being a video.
2. The first day, verbatim.
3. The early era, texture and one moment of unexpected kindness.
4. The peak, by volume.
5. The rupture or drift, honestly, without melodrama.
6. The repair, in full, with their messages doing the talking.
7. The long thinning, with the chart.
8. What they do now, in their own words. Acknowledge their actual work and life. This is
   the section people forget and the recipient notices most.
9. The recent ritual, in full.
10. Optional: something interactive the recipient can act on.
11. The letter.
12. The close, present tense, one image, one line.

Put a small scroll cue between acts. People stop scrolling long pages.

---

## Phase 6 — Review loop

Show copy in chat, in full, before it goes in the file. When the commissioner objects,
they are almost always right, and the objection is usually one of:

- A fact you inferred that is wrong.
- A feeling you assigned them that they do not have.
- Prose that sounds like a report rather than a person.
- A detail that is technically true and socially wrong.

After each pass, proactively list any remaining lines that assert something you cannot
source, and ask for keep / kill / reword on each. This surfaces problems faster than
waiting for them to be spotted.

---

## Phase 7 — Photographs

Ask for photos, and then **ask for the timestamp of each one**. This is the highest-value
question in the whole process. File dates routinely reveal that a photo was taken on a day
the two of them were together, and cross-referencing that against the chat produces facts
neither person has consciously noticed. In one run, three of seven photos turned out to be
from days they met, and the most recent was the last time that ever happened.

- Put the date in the caption. It does the emotional work for free.
- Caption in the recipient's own words wherever possible.
- Treat them as film stills: warm grade, fine grain, slight rotation, small numbered
  caption. Straighten on hover.
- Strip EXIF. Two of four photos in one run carried GPS.
- Do not generate AI imagery unless the recipient is known to be fine with it. Ask. If they
  are, the right move is usually for the commissioner to generate it, not you.

---

## Phase 8 — Build

Start from `templates/page.html`. It ships with the message rendering, the reveal system,
the photo frame, the picker and the print letter already solved.

Render messages as **the actual chat app**, not generic bubbles. See
`references/whatsapp-ui.md` for exact colours, tails, timestamp placement and tick marks.
The difference between "chat-like bubbles" and a real WhatsApp block is the difference
between a slideshow and a document.

QA with `scripts/capture.py`, which works around Chromium's screenshot ceiling. Read
`references/gotchas.md` first; it will save you an hour.

---

## Phase 9 — Deliver

Deploy per `references/deploy.md`. A private link on a domain the commissioner owns beats
a file attachment.

For the printed letter, use `templates/letter.html`. Local handwriting fonts only, because
`--print-to-pdf` does not wait for webfonts. White background, dark ink, so printing is
cheap. Adapt any line that refers to "this page" for print.

---

## Optional: something to act on

If the archive contains a recurring act of service, close the loop with an interactive
element. In one run the recipient had sent a cake across the country, and the page ended
with five food options drawn from things she had said she liked over ten years, each with
its date and quote, that messaged the commissioner over a Discord webhook when tapped.

Rules: every option must be evidenced with a date, it must degrade gracefully with no
webhook configured, and tell the commissioner to delete the webhook afterwards because the
URL is readable in the page source.

---

## Anti-patterns, all observed for real

| Do not | Instead |
|---|---|
| "22.7% of messages were sent after midnight" | Quote one 3am message |
| "You used 😂 3,500 times" | Cut it |
| "I read all ten years of our messages" | "Our whole chat is still on my phone. I went digging through it" |
| "I was the one who could not let it go" | Say only what they typed |
| "I remember being properly proud of you" | Find what they actually wrote at the time |
| Explaining the recipient's own joke in a caption | Their caption, verbatim, nothing else |
| A chat screenshot of something from last week | They were there. Cut it |
| Two paragraphs of the commissioner's self-analysis | Two sentences |
| Claiming a promise was kept without checking | Grep the outcome |
| Generic grey chat bubbles | The real app's colours and geometry |

---

## Files

- `scripts/parse_chat.py` — parse, measure, chunk
- `scripts/verify_quotes.py` — quote verification gate
- `scripts/capture.py` — screenshot QA past the 16384px cap
- `templates/page.html` — the page scaffold
- `templates/letter.html` — the printable letter
- `references/whatsapp-ui.md` — exact message rendering spec
- `references/gotchas.md` — tooling landmines
- `references/deploy.md` — Cloudflare Pages and custom domain
