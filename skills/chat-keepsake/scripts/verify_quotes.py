#!/usr/bin/env python3
"""
The accuracy gate. Pulls every quoted message out of a built keepsake page and
checks each one against the raw chat export.

    python3 verify_quotes.py site/index.html "WhatsApp Chat with X.txt"
    python3 verify_quotes.py site/index.html export.txt --strict   # exit 1 on any miss

Checks:
  * every .bub message bubble
  * every <blockquote> pull quote

Why this exists: sub-agents reading a large export reliably paraphrase, reorder and
merge exchanges without flagging it. In one run, roughly one quote in ten came back
with the message order or the speaker wrong. A gift built on a misquote is worse than
no gift, so this runs before every deploy.

Not a linter. A miss means go and read the raw export around that line.
"""

import argparse
import html
import re
import sys
import unicodedata

# --------------------------------------------------------------------------- #


def strip_tags(s):
    s = re.sub(r"<br\s*/?>", "\u241e", s, flags=re.I)   # RS: message separator
    s = re.sub(r"<span class=\"t\">.*?</span>", "", s, flags=re.S)  # timestamps
    s = re.sub(r"<cite.*?</cite>", "", s, flags=re.S)               # attributions
    s = re.sub(r"<[^>]+>", "", s)
    return html.unescape(s)


def norm(s):
    """Normalise for comparison without destroying the author's voice."""
    s = unicodedata.normalize("NFKC", s)
    s = s.replace("’", "'").replace("‘", "'")
    s = s.replace("“", '"').replace("”", '"')
    s = s.replace(" ", " ")
    s = re.sub(r"[ \t]+", " ", s)
    return s.strip()


def extract(page_html):
    """Return [(kind, text)] for every quoted string on the page."""
    out = []
    for m in re.finditer(r'<div class="bub[^"]*">(.*?)</div>', page_html, flags=re.S):
        t = norm(strip_tags(m.group(1)))
        if t:
            out.append(("bubble", t))
    for m in re.finditer(r"<blockquote[^>]*>(.*?)</blockquote>", page_html, flags=re.S):
        t = norm(strip_tags(m.group(1)))
        if t:
            out.append(("pullquote", t))
    return out


# lines that are narration inside a bubble, not a real message
DECORATIVE = re.compile(r"^(\[|—|\.\.\.|\d+ photograph|ten photograph|album)", re.I)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("page")
    ap.add_argument("export")
    ap.add_argument("--strict", action="store_true",
                    help="exit non-zero if anything fails to verify")
    ap.add_argument("--show-ok", action="store_true")
    a = ap.parse_args()

    page = open(a.page, encoding="utf-8", errors="replace").read()
    corpus = norm(open(a.export, encoding="utf-8", errors="replace").read())

    quotes = extract(page)
    if not quotes:
        sys.exit("No quotes found. Has the page markup changed?")

    ok, miss, skipped = [], [], []
    for kind, text in quotes:
        if DECORATIVE.match(text):
            skipped.append((kind, text))
            continue
        # a pull quote can hold several messages: split on the <br> separator,
        # then on any remaining wide gaps
        parts = []
        for seg in text.split("\u241e"):
            parts.extend(re.split(r"\s{2,}", seg))
        parts = [p.strip() for p in parts] or [text]
        parts = [p for p in parts if len(p) > 1]
        bad = [p for p in parts if p not in corpus]
        if bad:
            miss.append((kind, text, bad))
        else:
            ok.append((kind, text))

    print(f"checked {len(quotes)} quoted strings from {a.page}")
    print(f"  verified : {len(ok)}")
    print(f"  skipped  : {len(skipped)}  (narration, not real messages)")
    print(f"  MISSING  : {len(miss)}")

    if a.show_ok:
        print("\n--- verified ---")
        for kind, t in ok:
            print(f"  [{kind}] {t[:90]}")

    if skipped:
        print("\n--- skipped (confirm these are meant to be narration) ---")
        for kind, t in skipped:
            print(f"  [{kind}] {t[:90]}")

    if miss:
        print("\n--- NOT FOUND IN THE EXPORT ---")
        for kind, t, bad in miss:
            print(f"\n  [{kind}] {t[:120]}")
            for b in bad:
                print(f"      no match: {b[:110]}")
        print("\nEach of these is either a typo, a paraphrase, or an invented line.")
        print("Grep the export around the claimed date and fix the page, not this script.")

    if miss and a.strict:
        sys.exit(1)


if __name__ == "__main__":
    main()
