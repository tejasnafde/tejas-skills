import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL = REPO_ROOT / "skills" / "synthetic-panel"
SCRIPT = SKILL / "scripts" / "panel.py"

spec = importlib.util.spec_from_file_location("panel", SCRIPT)
panel = importlib.util.module_from_spec(spec)
spec.loader.exec_module(panel)

# Five orthogonal anchor directions: score k lives on axis k.
AXES = [[1.0 if i == k else 0.0 for i in range(5)] for k in range(5)]


class ScoringMath(unittest.TestCase):
    def test_pmf_sums_to_one_and_peaks_at_closest_anchor(self):
        for k in range(5):
            v = [0.1] * 5
            v[k] = 1.0
            pmf = panel.pmf_for_set(v, AXES)
            self.assertAlmostEqual(sum(pmf), 1.0, places=9)
            self.assertEqual(pmf.index(max(pmf)), k)

    def test_lowest_anchor_gets_zero_without_epsilon(self):
        pmf = panel.pmf_for_set([0.0, 0.2, 0.4, 0.6, 1.0], AXES)
        self.assertEqual(pmf[0], 0.0)

    def test_equal_similarity_gives_uniform(self):
        pmf = panel.pmf_for_set([1.0] * 5, AXES)
        self.assertEqual(pmf, [0.2] * 5)

    def test_expected_score_moves_with_response(self):
        low = panel.expected_score(panel.pmf_for_set([1, 0.3, 0.1, 0, 0], AXES))
        high = panel.expected_score(panel.pmf_for_set([0, 0, 0.1, 0.3, 1], AXES))
        self.assertLess(low, 2.5)
        self.assertGreater(high, 3.5)

    def test_low_temperature_sharpens(self):
        v = [0.1, 0.2, 0.3, 0.5, 0.9]
        base = panel.pmf_for_set(v, AXES)
        sharp = panel.scale_pmf(base, 0.5)
        self.assertGreater(max(sharp), max(base))
        self.assertAlmostEqual(sum(sharp), 1.0, places=9)

    def test_temperature_applies_after_averaging(self):
        v = [0.1, 0.2, 0.3, 0.5, 0.9]
        flipped = list(reversed(AXES))
        mean = panel.pmf_mean_over_sets(v, [AXES, flipped])
        self.assertEqual(panel.pmf_mean_over_sets(v, [AXES, flipped], temperature=0.5),
                         panel.scale_pmf(mean, 0.5))

    def test_mean_over_sets_averages(self):
        flipped = list(reversed(AXES))
        pmf = panel.pmf_mean_over_sets([0, 0, 0.1, 0.3, 1], [AXES, flipped])
        self.assertAlmostEqual(panel.expected_score(pmf), 3.0, places=9)

    def test_bootstrap_is_deterministic_and_brackets_mean(self):
        vals = [2.1, 2.5, 3.0, 3.2, 3.9, 4.1, 2.8, 3.3]
        a = panel.bootstrap_ci(vals, seed=1)
        b = panel.bootstrap_ci(vals, seed=1)
        self.assertEqual(a, b)
        mean = sum(vals) / len(vals)
        self.assertLess(a[0], mean)
        self.assertGreater(a[1], mean)

    def test_rank_with_ties(self):
        rows = [
            {"id": "a", "mean": 3.5, "ci_low": 3.3, "ci_high": 3.7},
            {"id": "b", "mean": 3.4, "ci_low": 3.2, "ci_high": 3.6},
            {"id": "c", "mean": 2.0, "ci_low": 1.8, "ci_high": 2.2},
        ]
        ranked = panel.rank_with_ties(rows)
        self.assertEqual([(r["id"], r["rank"], r["tie_with_above"]) for r in ranked],
                         [("a", 1, False), ("b", 1, True), ("c", 3, False)])

    def test_ties_do_not_chain(self):
        # Each item overlaps its neighbour, but the last does not overlap the first.
        rows = [
            {"id": "a", "mean": 3.05, "ci_low": 2.74, "ci_high": 3.35},
            {"id": "b", "mean": 2.48, "ci_low": 2.15, "ci_high": 2.86},
            {"id": "c", "mean": 2.26, "ci_low": 1.99, "ci_high": 2.55},
            {"id": "d", "mean": 2.06, "ci_low": 1.89, "ci_high": 2.26},
        ]
        ranked = panel.rank_with_ties(rows)
        self.assertEqual([(r["id"], r["rank"]) for r in ranked],
                         [("a", 1), ("b", 1), ("c", 3), ("d", 3)])

    def test_controls_need_separated_intervals(self):
        self.assertTrue(panel.controls_ok({"ci_low": 3.0}, {"ci_high": 2.0}))
        self.assertFalse(panel.controls_ok({"ci_low": 2.5}, {"ci_high": 2.6}))


class Inputs(unittest.TestCase):
    def test_examples_are_valid(self):
        items = json.loads((SKILL / "examples" / "items.example.json").read_text())
        personas = json.loads((SKILL / "examples" / "personas.example.json").read_text())
        self.assertEqual(panel.validate_items(items), [])
        self.assertEqual(panel.validate_personas(personas), [])

    def test_missing_controls_rejected(self):
        errs = panel.validate_items({"items": [{"id": "a", "text": "x"}, {"id": "b", "text": "y"}]})
        self.assertTrue(any("controls.good" in e for e in errs))

    def test_anchor_sets_have_five_points(self):
        anchors = json.loads((SKILL / "scripts" / "anchors.json").read_text())
        for q in anchors["questions"].values():
            self.assertIn("ask", q)
            self.assertFalse(q["validated"])
            for s in q["sets"]:
                self.assertEqual(len(s), 5)


class EndToEndWithFakeModels(unittest.TestCase):
    """A fake writer and embedder: the reaction names its sentiment, and the
    embedder maps sentiment words to anchor axes. No network."""

    WORDS = ["never", "doubt", "maybe", "try", "love"]

    def fake_embed(self, texts):
        out = []
        for t in texts:
            t = t.lower()
            v = [0.05] * 5
            for k, w in enumerate(self.WORDS):
                if w in t:
                    v[k] = 1.0
            # anchors: map by position words used in anchors.json
            for k, keys in enumerate([("definitely not", "no interest", "no way"),
                                      ("probably would not", "not really", "doubt"),
                                      ("might or might not", "not sure", "maybe"),
                                      ("probably download", "likely try", "give it a try"),
                                      ("definitely download", "love this", "want this now")]):
                if any(x in t for x in keys):
                    v[k] = 1.0
            out.append(v)
        return out

    def fake_generate(self, prompt):
        if "SPAM" in prompt:
            return "I would never install this."
        if "GOOD" in prompt:
            return "I love it."
        return "Maybe I would try it."

    def data(self):
        items = {"context": "You see this app:",
                 "items": [{"id": "a", "text": "plain idea"}, {"id": "b", "text": "GOOD idea"}],
                 "controls": {"good": {"text": "GOOD control"}, "bad": {"text": "SPAM control"}}}
        personas = {"audience": "test users", "calibrated": False,
                    "personas": [{"id": f"p{i}", "description": f"person {i}"} for i in range(12)]}
        return items, personas

    def test_ranking_and_controls(self):
        items, personas = self.data()
        summary, reactions = panel.run_panel(items, personas, "download",
                                             self.fake_generate, self.fake_embed, workers=2)
        self.assertTrue(summary["controls_ok"])
        self.assertEqual([r["id"] for r in summary["ranking"]], ["b", "a"])
        self.assertEqual(summary["calibration_label"], "Not yet calibrated for test users")
        self.assertEqual(len(reactions), 4 * 12)
        md = panel.render_markdown(summary, {"writer": "fake", "embedder": "fake"})
        self.assertIn("Not yet calibrated", md)
        self.assertNotIn("INVALID RUN", md)

    def test_swapped_controls_invalidate_run(self):
        items, personas = self.data()
        items["controls"] = {"good": {"text": "SPAM a"}, "bad": {"text": "GOOD b"}}
        summary, _ = panel.run_panel(items, personas, "download",
                                     self.fake_generate, self.fake_embed, workers=2)
        self.assertFalse(summary["controls_ok"])
        self.assertIn("INVALID RUN", panel.render_markdown(summary, {"writer": "f", "embedder": "f"}))

    def test_too_many_failures_raise(self):
        items, personas = self.data()

        def broken(prompt):
            raise RuntimeError("quota")
        with self.assertRaises(RuntimeError):
            panel.run_panel(items, personas, "download", broken, self.fake_embed, workers=2)

    def test_cli_dry_run_needs_no_credentials(self):
        ex = SKILL / "examples"
        with tempfile.TemporaryDirectory() as d:
            r = subprocess.run([sys.executable, str(SCRIPT), "run",
                                "--items", str(ex / "items.example.json"),
                                "--personas", str(ex / "personas.example.json"),
                                "--out", d, "--dry-run"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("reactions", r.stderr)


if __name__ == "__main__":
    unittest.main()
