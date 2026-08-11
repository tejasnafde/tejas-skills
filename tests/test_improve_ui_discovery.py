import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "skills" / "improve-ui" / "scripts" / "discover_ui_skills.py"


class DiscoverUiSkillsTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def make_skill(
        self,
        root: Path,
        directory_name: str,
        *,
        name: str | None = None,
        description: str = "UI specialist.",
        frontmatter: str | None = None,
    ) -> Path:
        skill_dir = root / directory_name
        skill_dir.mkdir(parents=True)
        if frontmatter is None:
            frontmatter = (
                "---\n"
                f"name: {name or directory_name}\n"
                "description: >-\n"
                f"  {description}\n"
                "---\n\n"
                "# Test skill\n"
            )
        (skill_dir / "SKILL.md").write_text(frontmatter, encoding="utf-8")
        return skill_dir

    def discover(self, *roots: tuple[str, Path]) -> dict:
        self.assertTrue(SCRIPT.is_file(), f"discovery implementation missing: {SCRIPT}")
        command = [sys.executable, str(SCRIPT), "--format", "json"]
        for scope, root in roots:
            command.extend(["--root", f"{scope}={root}"])
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_discovers_future_skill_without_a_registry_change(self):
        skills_root = self.root / "skills"
        self.make_skill(
            skills_root,
            "future-interface-magic",
            description="Designs interfaces using a technique invented after improve-ui shipped.",
        )

        result = self.discover(("user", skills_root))

        self.assertEqual([skill["name"] for skill in result["skills"]], ["future-interface-magic"])
        self.assertIn("invented after improve-ui shipped", result["skills"][0]["description"])

    def test_deduplicates_symlinked_installations_by_real_path(self):
        source_root = self.root / "source"
        source_skill = self.make_skill(source_root, "motion-craft")
        linked_root = self.root / "linked"
        linked_root.mkdir()
        (linked_root / "motion-craft").symlink_to(source_skill, target_is_directory=True)

        result = self.discover(("user", source_root), ("codex-profile", linked_root))

        self.assertEqual(len(result["skills"]), 1)
        self.assertEqual(result["skills"][0]["real_path"], str(source_skill.resolve()))

    def test_prefers_the_earlier_scope_when_names_collide(self):
        repo_root = self.root / "repo"
        user_root = self.root / "user"
        repo_skill = self.make_skill(repo_root, "ui-review", description="Project-specific UI rules.")
        user_skill = self.make_skill(user_root, "ui-review", description="Generic UI rules.")
        profile_root = self.root / "profile"
        profile_root.mkdir()
        (profile_root / "ui-review").symlink_to(user_skill, target_is_directory=True)

        result = self.discover(("repo", repo_root), ("user", user_root), ("profile", profile_root))

        self.assertEqual(len(result["skills"]), 1)
        skill = result["skills"][0]
        self.assertEqual(skill["scope"], "repo")
        self.assertEqual(skill["real_path"], str(repo_skill.resolve()))
        self.assertEqual(skill["shadowed_paths"], [str(user_skill.resolve())])

    def test_skips_malformed_frontmatter_and_reports_a_warning(self):
        skills_root = self.root / "skills"
        self.make_skill(
            skills_root,
            "broken-skill",
            frontmatter="---\ndescription: Missing a name.\n---\n",
        )

        result = self.discover(("user", skills_root))

        self.assertEqual(result["skills"], [])
        self.assertEqual(len(result["warnings"]), 1)
        self.assertIn("missing name or description", result["warnings"][0])

    def test_excludes_improve_ui_itself(self):
        skills_root = self.root / "skills"
        self.make_skill(skills_root, "improve-ui", description="The orchestrator.")
        self.make_skill(skills_root, "frontend-design", description="The lead implementer.")

        result = self.discover(("user", skills_root))

        self.assertEqual([skill["name"] for skill in result["skills"]], ["frontend-design"])


if __name__ == "__main__":
    unittest.main()
