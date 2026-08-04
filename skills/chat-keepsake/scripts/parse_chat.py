#!/usr/bin/env python3
"""
Parse a chat export, compute the facts that carry narrative, and split it into
era chunks for parallel deep reading.

    python3 parse_chat.py "WhatsApp Chat with X.txt" --out work/

Outputs:
    work/parsed.jsonl        one message per line: {ts, who, text}
    work/stats.json          the numbers worth using
    work/chunks/NN_label.txt era chunks, roughly balanced by message count

Supports both WhatsApp export dialects:
    23/09/16, 6:39 pm - Name: text          (day-first, 12h, most of the world)
    9/23/16, 6:39 PM - Name: text           (month-first, US)
    [23/09/2016, 18:39:02] Name: text       (bracketed, iOS)
Continuation lines are stitched onto the previous message.
"""

import argparse
import collections
import datetime as dt
import json
import os
import re
import sys

# --------------------------------------------------------------------------- #
# parsing
# --------------------------------------------------------------------------- #

PATTERNS = [
    # 23/09/16, 6:39 pm - Sender: text     |  9/23/2016, 6:39 PM - Sender: text
    re.compile(
        r"^(?P<d1>\d{1,2})/(?P<d2>\d{1,2})/(?P<y>\d{2,4}),\s+"
        r"(?P<h>\d{1,2}):(?P<mi>\d{2})(?::(?P<s>\d{2}))?\s*"
        r"(?P<ap>[apAP]\.?[mM]\.?)?\s*-\s*"
        r"(?P<who>[^:]{1,60}?):\s(?P<text>.*)$"
    ),
    # [23/09/2016, 18:39:02] Sender: text
    re.compile(
        r"^\[(?P<d1>\d{1,2})/(?P<d2>\d{1,2})/(?P<y>\d{2,4}),\s+"
        r"(?P<h>\d{1,2}):(?P<mi>\d{2})(?::(?P<s>\d{2}))?\s*"
        r"(?P<ap>[apAP]\.?[mM]\.?)?\]\s*"
        r"(?P<who>[^:]{1,60}?):\s(?P<text>.*)$"
    ),
]

# a line that starts a new message at all (used for continuation detection)
STARTERS = [re.compile(r"^\d{1,2}/\d{1,2}/\d{2,4},\s"), re.compile(r"^\[\d{1,2}/\d{1,2}/\d{2,4},\s")]


def looks_like_start(line):
    return any(p.match(line) for p in STARTERS)


def detect_dayfirst(lines):
    """If any first component exceeds 12, it must be the day."""
    d1_max = d2_max = 0
    for ln in lines:
        for p in PATTERNS:
            m = p.match(ln)
            if m:
                d1_max = max(d1_max, int(m.group("d1")))
                d2_max = max(d2_max, int(m.group("d2")))
                break
    if d1_max > 12:
        return True
    if d2_max > 12:
        return False
    return True  # ambiguous: day-first is the global default


def parse(path):
    raw = open(path, encoding="utf-8", errors="replace").read().split("\n")
    dayfirst = detect_dayfirst(raw[:4000])
    msgs = []
    unmatched = 0

    for line in raw:
        if not line.strip():
            continue
        hit = None
        for p in PATTERNS:
            m = p.match(line)
            if m:
                hit = m
                break
        if not hit:
            if msgs and not looks_like_start(line):
                msgs[-1]["text"] += " " + line.strip()   # continuation
            else:
                unmatched += 1                            # system notice
            continue

        g = hit.groupdict()
        d1, d2 = int(g["d1"]), int(g["d2"])
        day, mon = (d1, d2) if dayfirst else (d2, d1)
        year = int(g["y"])
        if year < 100:
            year += 2000
        hour = int(g["h"])
        ap = (g.get("ap") or "").lower().replace(".", "")
        if ap == "pm" and hour != 12:
            hour += 12
        elif ap == "am" and hour == 12:
            hour = 0
        try:
            ts = dt.datetime(year, mon, day, hour, int(g["mi"]), int(g.get("s") or 0))
        except ValueError:
            unmatched += 1
            continue
        msgs.append({"ts": ts, "who": g["who"].strip(), "text": g["text"]})

    msgs.sort(key=lambda m: m["ts"])
    return msgs, unmatched, dayfirst


# --------------------------------------------------------------------------- #
# stats that carry story
# --------------------------------------------------------------------------- #

MEDIA_MARKERS = ("<media omitted>", "image omitted", "video omitted",
                 "sticker omitted", "audio omitted", "document omitted",
                 "gif omitted")


def is_media(text):
    t = text.lower()
    return any(m in t for m in MEDIA_MARKERS)


def stats(msgs):
    if not msgs:
        return {}

    per_person = collections.Counter(m["who"] for m in msgs)
    days = sorted({m["ts"].date() for m in msgs})

    # silences
    gaps = []
    for i in range(len(days) - 1):
        n = (days[i + 1] - days[i]).days
        if n > 1:
            gaps.append({"days": n, "from": str(days[i]), "to": str(days[i + 1])})
    gaps.sort(key=lambda g: -g["days"])

    # longest consecutive-day streak
    best = cur = 1
    b_start = c_start = days[0]
    b_end = days[0]
    for i in range(1, len(days)):
        if (days[i] - days[i - 1]).days == 1:
            cur += 1
            if cur > best:
                best, b_start, b_end = cur, c_start, days[i]
        else:
            cur, c_start = 1, days[i]

    by_day = collections.Counter(m["ts"].date() for m in msgs)
    by_year = collections.Counter(m["ts"].year for m in msgs)
    by_month = collections.Counter(m["ts"].strftime("%Y-%m") for m in msgs)

    # who breaks each long silence: the single most affecting computed fact
    breakers = []
    for g in gaps[:12]:
        to = dt.date.fromisoformat(g["to"])
        first = next((m for m in msgs if m["ts"].date() == to), None)
        if first:
            breakers.append({"after_days": g["days"], "on": g["to"],
                             "who": first["who"], "text": first["text"][:120]})
    who_breaks = collections.Counter(b["who"] for b in breakers)

    return {
        "total": len(msgs),
        "per_person": dict(per_person.most_common()),
        "first": msgs[0]["ts"].isoformat(),
        "last": msgs[-1]["ts"].isoformat(),
        "days_elapsed": (msgs[-1]["ts"] - msgs[0]["ts"]).days,
        "days_with_messages": len(days),
        "longest_silences": gaps[:12],
        "longest_daily_streak": {"days": best, "from": str(b_start), "to": str(b_end)},
        "busiest_days": [{"date": str(d), "count": c} for d, c in by_day.most_common(10)],
        "busiest_months": [{"month": m, "count": c} for m, c in by_month.most_common(12)],
        "by_year": dict(sorted(by_year.items())),
        "media_count": sum(1 for m in msgs if is_media(m["text"])),
        "silence_breakers": breakers,
        "who_speaks_first_after_silence": dict(who_breaks.most_common()),
        "_note": "Use silences, streaks, busiest days, per-year decline and "
                 "who_speaks_first_after_silence. Skip percentages and emoji counts.",
    }


# --------------------------------------------------------------------------- #
# chunking for parallel readers
# --------------------------------------------------------------------------- #

def chunk(msgs, out_dir, n_chunks):
    """Greedily pack month buckets into balanced chunks on era boundaries.

    Packing whole years overshoots badly when one year dominates the archive
    (one real export had 11,550 messages in a single year against a 5,967 target),
    so buckets are monthly and chunks break at the nearest month.
    """
    os.makedirs(out_dir, exist_ok=True)

    buckets = collections.OrderedDict()
    for m in msgs:
        buckets.setdefault((m["ts"].year, m["ts"].month), []).append(m)

    target = max(1, len(msgs) / n_chunks)
    chunks, cur = [], []
    for key, group in buckets.items():
        # start a new chunk when the current one is closer to target without this
        # bucket than with it, and there is still room for more chunks
        if cur and len(chunks) < n_chunks - 1:
            if abs(len(cur) - target) <= abs(len(cur) + len(group) - target):
                chunks.append(cur)
                cur = []
        cur.extend(group)
    if cur:
        chunks.append(cur)

    written = []
    for i, group in enumerate(chunks, 1):
        a, b = group[0]["ts"], group[-1]["ts"]
        label = a.strftime("%Y%m") + ("" if (a.year, a.month) == (b.year, b.month)
                                      else "-" + b.strftime("%Y%m"))
        path = os.path.join(out_dir, f"{i:02d}_{label}.txt")
        with open(path, "w", encoding="utf-8") as fh:
            for m in group:
                hour12 = m["ts"].hour % 12 or 12
                ampm = "am" if m["ts"].hour < 12 else "pm"
                fh.write(f"{m['ts'].strftime('%d/%m/%y')}, {hour12}:"
                         f"{m['ts'].strftime('%M')} {ampm} - "
                         f"{m['who']}: {m['text']}\n")
        written.append({"file": os.path.basename(path),
                        "span": f"{a.date()} to {b.date()}",
                        "messages": len(group)})
    return written


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("export")
    ap.add_argument("--out", default="work")
    ap.add_argument("--chunks", type=int, default=6)
    a = ap.parse_args()

    msgs, unmatched, dayfirst = parse(a.export)
    if not msgs:
        sys.exit("No messages parsed. Check the export format against PATTERNS.")

    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "parsed.jsonl"), "w", encoding="utf-8") as fh:
        for m in msgs:
            fh.write(json.dumps({"ts": m["ts"].isoformat(), "who": m["who"],
                                 "text": m["text"]}, ensure_ascii=False) + "\n")

    s = stats(msgs)
    s["parse"] = {"messages": len(msgs), "unmatched_lines": unmatched,
                  "day_first_dates": dayfirst}
    s["chunks"] = chunk(msgs, os.path.join(a.out, "chunks"), a.chunks)
    json.dump(s, open(os.path.join(a.out, "stats.json"), "w"), indent=2, default=str)

    print(f"parsed {len(msgs)} messages ({unmatched} unmatched), "
          f"day-first dates: {dayfirst}")
    print(f"span {s['first'][:10]} to {s['last'][:10]}  "
          f"({s['days_elapsed']} days, talked on {s['days_with_messages']})")
    print("per person:", s["per_person"])
    print("\nlongest silences:")
    for g in s["longest_silences"][:5]:
        print(f"  {g['days']:>4}d  {g['from']} -> {g['to']}")
    print("\nwho speaks first after a silence:", s["who_speaks_first_after_silence"])
    print("\nby year:", s["by_year"])
    print("\nchunks:")
    for c in s["chunks"]:
        print(f"  {c['file']:<22} {c['messages']:>6} msgs")
    print(f"\n-> {a.out}/stats.json")


if __name__ == "__main__":
    main()
