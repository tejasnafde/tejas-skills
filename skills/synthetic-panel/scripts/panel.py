"""Synthetic customer panel: rank ideas with persona reactions scored by
Semantic Similarity Rating (SSR, arXiv 2510.08338).

Each persona sees one item and writes a short free-text reaction. The reaction is
embedded and compared with five anchor statements (one per score 1-5) in several
anchor sets. Similarity becomes a probability for each score, averaged over the
sets. Items are ranked by their mean expected score, with a bootstrap interval.

The scoring follows pymc-labs/semantic-similarity-rating (Apache-2.0):
gamma = (1 + cos) / 2, subtract the minimum over the five points, normalise,
then optional temperature scaling. Temperature 1 and epsilon 0 are the defaults.

Usage:
  uv run -q --with google-genai python panel.py run \
      --items items.json --personas personas.json --out runs/2026-11-23 \
      [--question download] [--writer gemini-3.5-flash-lite] \
      [--embedder gemini-embedding-001] [--project P] [--location global] \
      [--log calibration.jsonl] [--dry-run]

Credentials: Application Default Credentials or GOOGLE_APPLICATION_CREDENTIALS
pointing to a key with roles/aiplatform.user on the project. The project comes
from --project or GOOGLE_CLOUD_PROJECT.

Exit codes: 0 ok, 1 error, 2 controls failed (the ranking is not valid).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
import random
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ANCHORS_FILE = HERE / "anchors.json"
DEFAULT_WRITER = "gemini-3.5-flash-lite"
DEFAULT_EMBEDDER = "gemini-embedding-001"
# Embedders that merge a list of inputs into one vector: send one text per call.
ONE_TEXT_PER_CALL = {"gemini-embedding-2"}


# ---------------------------------------------------------------- scoring math

def normalize(v):
    n = math.sqrt(sum(x * x for x in v))
    return [x / n for x in v] if n else list(v)


def cosine(a, b):
    return sum(x * y for x, y in zip(normalize(a), normalize(b)))


def pmf_for_set(response_vec, anchor_vecs, epsilon=0.0):
    """Probability of each score 1..N for one response against one anchor set."""
    gammas = [(1 + cosine(response_vec, a)) / 2 for a in anchor_vecs]
    low = min(gammas)
    vals = [g - low for g in gammas]
    vals[gammas.index(low)] += epsilon
    total = sum(vals)
    if total <= 0:
        return [1 / len(vals)] * len(vals)
    return [v / total for v in vals]


def scale_pmf(pmf, temperature):
    """Temperature scaling as in the reference code: p ** (1 / T), renormalised."""
    if temperature == 1.0:
        return list(pmf)
    if temperature <= 0:
        out = [0.0] * len(pmf)
        out[pmf.index(max(pmf))] = 1.0
        return out
    powered = [p ** (1 / temperature) for p in pmf]
    s = sum(powered)
    return [p / s for p in powered]


def pmf_mean_over_sets(response_vec, anchor_sets, temperature=1.0, epsilon=0.0):
    """Average over anchor sets first, then scale, as the reference code does."""
    pmfs = [pmf_for_set(response_vec, s, epsilon) for s in anchor_sets]
    return scale_pmf([sum(col) / len(pmfs) for col in zip(*pmfs)], temperature)


def expected_score(pmf):
    return sum((i + 1) * p for i, p in enumerate(pmf))


def bootstrap_ci(values, n_boot=2000, alpha=0.10, seed=0):
    """Percentile bootstrap interval for the mean."""
    if len(values) < 2:
        m = values[0] if values else float("nan")
        return (m, m)
    rng = random.Random(seed)
    k = len(values)
    means = sorted(sum(rng.choice(values) for _ in range(k)) / k for _ in range(n_boot))
    lo = means[int(alpha / 2 * n_boot)]
    hi = means[min(n_boot - 1, int((1 - alpha / 2) * n_boot))]
    return (lo, hi)


def rank_with_ties(rows):
    """rows: dicts with mean, ci_low, ci_high. Sort by mean, best first. An item
    whose interval overlaps the interval of the first item of the current rank
    group shares that rank. Comparing with the group leader, not the item just
    above, stops ties from chaining down the whole list."""
    ordered = sorted(rows, key=lambda r: r["mean"], reverse=True)
    leader = None
    for i, r in enumerate(ordered):
        if leader is None or r["ci_high"] < leader["ci_low"]:
            leader = r
            r["rank"] = i + 1
            r["tie_with_above"] = False
        else:
            r["rank"] = leader["rank"]
            r["tie_with_above"] = True
    return ordered


def controls_ok(good, bad):
    """The known-good control must score clearly above the known-bad one."""
    return good["ci_low"] > bad["ci_high"]


# ---------------------------------------------------------------- inputs

def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_items(data):
    errors = []
    items = data.get("items") or []
    if not 2 <= len(items) <= 15:
        errors.append("items: give 2 to 15 items (5 to 10 is the sweet spot)")
    controls = data.get("controls") or {}
    for key in ("good", "bad"):
        c = controls.get(key) or {}
        if not c.get("text"):
            errors.append(f"controls.{key}.text is required")
    ids = [i.get("id") for i in items] + [f"control_{k}" for k in ("good", "bad")]
    if len(set(ids)) != len(ids) or not all(ids):
        errors.append("every item needs a unique id")
    if not all(i.get("text") for i in items):
        errors.append("every item needs text")
    return errors


def validate_personas(data):
    errors = []
    ps = data.get("personas") or []
    if len(ps) < 10:
        errors.append("personas: give at least 10 (30 to 50 is better)")
    if not data.get("audience"):
        errors.append("audience is required, for example 'urban India Android users'")
    if not all(p.get("description") for p in ps):
        errors.append("every persona needs a description")
    return errors


def build_prompt(persona, context, item_text, question):
    return (
        f"You are this person: {persona}.\n\n"
        f"{context}\n\n\"{item_text}\"\n\n"
        f"In 2 to 4 sentences, say honestly how you react to it and {question['ask']}. "
        "Speak as yourself, in plain words, the way you would talk. Do not give a number or a rating."
    )


def plan_jobs(items_data, personas_data, per_item, reps, seed):
    all_items = [dict(i) for i in items_data["items"]]
    for key in ("good", "bad"):
        c = dict(items_data["controls"][key])
        c["id"] = f"control_{key}"
        c["control"] = key
        all_items.append(c)
    personas = personas_data["personas"]
    n = min(per_item or len(personas), len(personas))
    rng = random.Random(seed)
    jobs = []
    for rep in range(reps):
        for item in all_items:
            for p in rng.sample(personas, n):
                jobs.append({"rep": rep, "item": item, "persona": p})
    rng.shuffle(jobs)
    return all_items, jobs


# ---------------------------------------------------------------- model calls

class Vertex:
    def __init__(self, project, location, writer, embedder, temperature):
        from google import genai
        from google.genai import types

        self.types = types
        self.client = genai.Client(vertexai=True, project=project, location=location)
        self.writer, self.embedder, self.temperature = writer, embedder, temperature
        self.tokens_in = self.tokens_out = 0

    def generate(self, prompt):
        cfg = self.types.GenerateContentConfig(
            temperature=self.temperature, max_output_tokens=2000,
            labels={"app": "synthetic-panel"},
        )
        last = None
        for attempt in range(4):
            try:
                r = self.client.models.generate_content(model=self.writer, contents=prompt, config=cfg)
                u = r.usage_metadata
                if u:
                    self.tokens_in += u.prompt_token_count or 0
                    self.tokens_out += (u.candidates_token_count or 0) + (getattr(u, "thoughts_token_count", 0) or 0)
                text = (r.text or "").strip()
                if text:
                    return text
                last = "empty reply"
            except Exception as e:  # network, quota, safety block
                last = str(e)[:200]
            time.sleep(2 ** attempt)
        raise RuntimeError(last)

    def embed(self, texts):
        step = 1 if self.embedder in ONE_TEXT_PER_CALL else 50
        out = []
        for i in range(0, len(texts), step):
            r = self.client.models.embed_content(model=self.embedder, contents=texts[i:i + step])
            out += [list(e.values) for e in r.embeddings]
        if len(out) != len(texts):
            raise RuntimeError(f"embedder returned {len(out)} vectors for {len(texts)} texts")
        return out


# ---------------------------------------------------------------- run

def run_panel(items_data, personas_data, question_key, generate, embed, *,
              per_item=0, reps=1, seed=0, workers=8, anchors=None):
    """Core run with injected generate(prompt)->str and embed(list)->list[vec].
    Returns (summary, reactions)."""
    anchors = anchors or load_json(ANCHORS_FILE)
    question = anchors["questions"][question_key]
    all_items, jobs = plan_jobs(items_data, personas_data, per_item, reps, seed)
    context = items_data.get("context", "You see this:")

    def one(job):
        prompt = build_prompt(job["persona"]["description"], context, job["item"]["text"], question)
        try:
            return generate(prompt), None
        except Exception as e:
            return None, str(e)

    with ThreadPoolExecutor(workers) as ex:
        results = list(ex.map(one, jobs))

    ok = [(j, t) for j, (t, err) in zip(jobs, results) if t]
    failed = len(jobs) - len(ok)
    if failed > 0.1 * len(jobs):
        raise RuntimeError(f"{failed} of {len(jobs)} generations failed; first error: "
                           f"{next(err for _, err in results if err)}")

    anchor_sets = [embed(s) for s in question["sets"]]
    vecs = embed([t for _, t in ok])
    reactions = []
    for (job, text), v in zip(ok, vecs):
        pmf = pmf_mean_over_sets(v, anchor_sets)
        reactions.append({
            "item_id": job["item"]["id"], "rep": job["rep"],
            "persona_id": job["persona"].get("id"), "persona": job["persona"]["description"],
            "reaction": text, "pmf": [round(p, 4) for p in pmf], "score": round(expected_score(pmf), 4),
        })

    rows = []
    for item in all_items:
        mine = [r for r in reactions if r["item_id"] == item["id"]]
        scores = [r["score"] for r in mine]
        lo, hi = bootstrap_ci(scores, seed=seed)
        dist = [round(sum(r["pmf"][k] for r in mine) / max(1, len(mine)), 3) for k in range(5)]
        rows.append({"id": item["id"], "text": item["text"], "control": item.get("control"),
                     "n": len(scores), "mean": round(sum(scores) / max(1, len(scores)), 3),
                     "ci_low": round(lo, 3), "ci_high": round(hi, 3), "distribution": dist})

    good = next(r for r in rows if r["control"] == "good")
    bad = next(r for r in rows if r["control"] == "bad")
    ranked = rank_with_ties([r for r in rows if not r["control"]])
    calibrated = bool(personas_data.get("calibrated"))
    summary = {
        "date": dt.date.today().isoformat(),
        "question": question_key, "anchors_validated": bool(question.get("validated")),
        "audience": personas_data["audience"], "calibrated": calibrated,
        "calibration_label": None if calibrated else f"Not yet calibrated for {personas_data['audience']}",
        "controls_ok": controls_ok(good, bad), "control_good": good, "control_bad": bad,
        "failed_generations": failed, "ranking": ranked,
    }
    return summary, reactions


def render_markdown(summary, meta):
    lines = [f"# Synthetic panel: {summary['date']}", ""]
    if not summary["controls_ok"]:
        lines += ["**INVALID RUN: the good control did not score clearly above the bad control. "
                  "Do not use this ranking.**", ""]
    if summary["calibration_label"]:
        lines += [f"*{summary['calibration_label']}.*", ""]
    if not summary["anchors_validated"]:
        lines += [f"*Anchor set '{summary['question']}' is not validated against human ratings.*", ""]
    lines += ["Ranks compare these items with one another. A score is not a forecast of "
              "installs, conversion or revenue.", "",
              "| Rank | Item | Mean (1-5) | 90% interval | n |", "|---|---|---|---|---|"]
    for r in summary["ranking"]:
        rank = f"{r['rank']}{' (tie)' if r['tie_with_above'] else ''}"
        lines.append(f"| {rank} | {r['text'][:80]} | {r['mean']:.2f} | "
                     f"{r['ci_low']:.2f} to {r['ci_high']:.2f} | {r['n']} |")
    g, b = summary["control_good"], summary["control_bad"]
    lines += ["", f"Controls: good {g['mean']:.2f} ({g['ci_low']:.2f} to {g['ci_high']:.2f}), "
                  f"bad {b['mean']:.2f} ({b['ci_low']:.2f} to {b['ci_high']:.2f}).",
              f"Writer {meta['writer']}, embedder {meta['embedder']}, audience: {summary['audience']}, "
              f"failed generations: {summary['failed_generations']}."]
    return "\n".join(lines) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--items", required=True)
    r.add_argument("--personas", required=True)
    r.add_argument("--out", required=True)
    r.add_argument("--question", default="download")
    r.add_argument("--writer", default=DEFAULT_WRITER)
    r.add_argument("--embedder", default=DEFAULT_EMBEDDER)
    r.add_argument("--project", default=os.environ.get("GOOGLE_CLOUD_PROJECT"))
    r.add_argument("--location", default="global")
    r.add_argument("--per-item", type=int, default=0, help="personas per item (default: all)")
    r.add_argument("--reps", type=int, default=1)
    r.add_argument("--temperature", type=float, default=0.5)
    r.add_argument("--seed", type=int, default=0)
    r.add_argument("--workers", type=int, default=8)
    r.add_argument("--log", help="append a one-line run record to this calibration log")
    r.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)

    items, personas = load_json(a.items), load_json(a.personas)
    anchors = load_json(ANCHORS_FILE)
    errors = validate_items(items) + validate_personas(personas)
    if a.question not in anchors["questions"]:
        errors.append(f"--question must be one of {sorted(anchors['questions'])}")
    if errors:
        print("\n".join("error: " + e for e in errors), file=sys.stderr)
        return 1
    _, jobs = plan_jobs(items, personas, a.per_item, a.reps, a.seed)
    print(f"{len(jobs)} reactions: {len(items['items'])} items + 2 controls, "
          f"{len(jobs) // (len(items['items']) + 2)} per item.", file=sys.stderr)
    if a.dry_run:
        return 0
    if not a.project:
        print("error: set --project or GOOGLE_CLOUD_PROJECT", file=sys.stderr)
        return 1

    vx = Vertex(a.project, a.location, a.writer, a.embedder, a.temperature)
    try:
        summary, reactions = run_panel(items, personas, a.question, vx.generate, vx.embed,
                                       per_item=a.per_item, reps=a.reps, seed=a.seed,
                                       workers=a.workers, anchors=anchors)
    except RuntimeError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    meta = {"writer": a.writer, "embedder": a.embedder, "temperature": a.temperature,
            "seed": a.seed, "tokens_in": vx.tokens_in, "tokens_out": vx.tokens_out}
    summary["meta"] = meta
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "reactions.jsonl").write_text(
        "".join(json.dumps(x, ensure_ascii=False) + "\n" for x in reactions), encoding="utf-8")
    (out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    md = render_markdown(summary, meta)
    (out / "summary.md").write_text(md, encoding="utf-8")
    if a.log:
        rec = {"date": summary["date"], "run": str(out), "question": a.question,
               "audience": summary["audience"], "writer": a.writer, "embedder": a.embedder,
               "controls_ok": summary["controls_ok"],
               "ranking": [[x["id"], x["rank"], x["mean"]] for x in summary["ranking"]],
               "outcome": None}
        with open(a.log, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(md)
    return 0 if summary["controls_ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
