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
the raw export yourself and read the surrounding twenty lines. `references/gotchas.md`
documents the observed failure modes.

Once the page exists:

```bash
python3 scripts/verify_quotes.py site/index.html "<export.txt>"
```

It pulls every message bubble and pull-quote out of the HTML and checks each against the
export. Do not deploy with misses.

---

## Phase 4 — Find the spine

A keepsake needs one thread, not a list of highlights: a surviving phrase, a reversal, a
promise never kept, a prediction that came true. Read `references/writing.md` before
drafting, and tell the commissioner the spine you found before writing to it.

---

## Phase 5 — Draft

Numbers, voice, and the chapter structure that works are all in `references/writing.md`,
along with the anti-patterns table. Read it before drafting. The short version: keep only
numbers that carry story, let the messages do the emotional work, and end in the present
tense.

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
- Strip EXIF from every photo, per Hard rule 7.
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

## Files

- `scripts/parse_chat.py` — parse, measure, chunk
- `scripts/verify_quotes.py` — quote verification gate
- `scripts/capture.py` — screenshot QA past the 16384px cap
- `templates/page.html` — the page scaffold
- `templates/letter.html` — the printable letter
- `references/writing.md` - the spine, numbers, voice, structure, and anti-patterns
- `references/whatsapp-ui.md` — exact message rendering spec
- `references/gotchas.md` — tooling landmines
- `references/deploy.md` — Cloudflare Pages and custom domain
