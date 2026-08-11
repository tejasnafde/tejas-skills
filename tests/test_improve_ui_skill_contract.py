import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_FILE = REPO_ROOT / "skills" / "improve-ui" / "SKILL.md"
OPENAI_FILE = REPO_ROOT / "skills" / "improve-ui" / "agents" / "openai.yaml"
README_FILE = REPO_ROOT / "README.md"


class ImproveUiSkillContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL_FILE.read_text(encoding="utf-8")
        cls.openai = OPENAI_FILE.read_text(encoding="utf-8")
        cls.readme = README_FILE.read_text(encoding="utf-8")

    def test_skill_is_complete_and_explicit_only(self):
        self.assertNotIn("TODO", self.skill)
        self.assertIn("name: improve-ui", self.skill)
        frontmatter = self.skill.split("---", 2)[1]
        self.assertNotIn("disable-model-invocation", frontmatter)
        self.assertIn("only when explicitly invoked", self.skill.lower())
        self.assertIn("allow_implicit_invocation: false", self.openai)

    def test_skill_dynamically_discovers_and_bounds_its_wand_stack(self):
        self.assertIn("scripts/discover_ui_skills.py", self.skill)
        self.assertIn("one lead", self.skill.lower())
        self.assertIn("at most three specialists", self.skill.lower())
        self.assertIn("read its `skill.md` completely", self.skill.lower())
        self.assertIn("future", self.skill.lower())

    def test_skill_requires_baseline_visual_inspection_and_iteration(self):
        self.assertIn("before editing", self.skill.lower())
        self.assertIn("responsive", self.skill.lower())
        self.assertIn("accessibility", self.skill.lower())
        self.assertIn("iterate", self.skill.lower())

    def test_skill_limits_authority_and_handles_fallbacks(self):
        self.assertIn("do not install", self.skill.lower())
        self.assertIn("dirty worktree", self.skill.lower())
        self.assertIn("visual tooling", self.skill.lower())

    def test_readme_lists_the_skill(self):
        self.assertIn("[improve-ui](./skills/improve-ui/SKILL.md)", self.readme)
        self.assertIn("/improve-ui", self.readme)


if __name__ == "__main__":
    unittest.main()
