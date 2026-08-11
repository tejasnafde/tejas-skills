#!/usr/bin/env python3
"""Inventory available skills without loading their full instructions."""

from __future__ import annotations

import argparse
import ast
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


SELF_NAME = "improve-ui"


@dataclass(frozen=True)
class RootSpec:
    scope: str
    path: Path


def _scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        try:
            parsed = ast.literal_eval(value)
            return parsed if isinstance(parsed, str) else str(parsed)
        except (SyntaxError, ValueError):
            return value[1:-1]
    return value


def parse_frontmatter(path: Path) -> tuple[str, str] | None:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return None

    try:
        end = next(index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration:
        return None

    metadata: dict[str, str] = {}
    index = 1
    while index < end:
        line = lines[index]
        if not line or line[0].isspace() or ":" not in line:
            index += 1
            continue

        key, raw_value = line.split(":", 1)
        key = key.strip()
        raw_value = raw_value.strip()
        if key not in {"name", "description"}:
            index += 1
            continue

        if raw_value in {">", ">-", ">+", "|", "|-", "|+"}:
            block: list[str] = []
            index += 1
            while index < end and (not lines[index] or lines[index][0].isspace()):
                block.append(lines[index].strip())
                index += 1
            if raw_value.startswith(">"):
                metadata[key] = " ".join(part for part in block if part).strip()
            else:
                metadata[key] = "\n".join(block).strip()
            continue

        metadata[key] = _scalar(raw_value)
        index += 1

    name = metadata.get("name", "").strip()
    description = metadata.get("description", "").strip()
    if not name or not description:
        return None
    return name, description


def _repo_skill_roots(cwd: Path) -> list[RootSpec]:
    roots: list[RootSpec] = []
    current = cwd.resolve()
    repo_root: Path | None = None
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            repo_root = candidate
            break

    if repo_root is None:
        candidate = current / ".agents" / "skills"
        return [RootSpec("repo", candidate)] if candidate.is_dir() else []

    candidate = current
    while True:
        skill_root = candidate / ".agents" / "skills"
        if skill_root.is_dir():
            roots.append(RootSpec(f"repo:{candidate}", skill_root))
        if candidate == repo_root:
            break
        candidate = candidate.parent
    return roots


def default_roots(cwd: Path) -> list[RootSpec]:
    home = Path.home()
    roots = _repo_skill_roots(cwd)
    roots.append(RootSpec("user", home / ".agents" / "skills"))

    codex_home = Path(os.environ.get("CODEX_HOME", home / ".codex"))
    roots.append(RootSpec("codex", codex_home / "skills"))
    if codex_home != home / ".codex":
        roots.append(RootSpec("codex-default", home / ".codex" / "skills"))
    roots.extend(RootSpec(f"codex-profile:{path.parent.name}", path) for path in sorted(home.glob(".codex-*/skills")))

    roots.append(RootSpec("claude", home / ".claude" / "skills"))
    roots.extend(RootSpec(f"claude-profile:{path.parent.name}", path) for path in sorted(home.glob(".claude-*/skills")))
    return roots


def parse_root_specs(values: Iterable[str]) -> list[RootSpec]:
    specs: list[RootSpec] = []
    for index, value in enumerate(values):
        if "=" in value:
            scope, raw_path = value.split("=", 1)
        else:
            scope, raw_path = f"explicit-{index}", value
        specs.append(RootSpec(scope.strip() or f"explicit-{index}", Path(raw_path).expanduser()))
    return specs


def discover(roots: Iterable[RootSpec]) -> dict[str, list]:
    skills_by_name: dict[str, dict] = {}
    skills_by_real_path: dict[str, dict] = {}
    warnings: list[str] = []
    seen_roots: set[str] = set()
    seen_real_paths: set[str] = set()

    for root in roots:
        if not root.path.is_dir():
            continue
        resolved_root = str(root.path.resolve())
        if resolved_root in seen_roots:
            continue
        seen_roots.add(resolved_root)

        for candidate in sorted(root.path.iterdir(), key=lambda item: item.name):
            skill_file = candidate / "SKILL.md"
            if not skill_file.is_file():
                continue
            try:
                metadata = parse_frontmatter(skill_file)
            except (OSError, UnicodeError) as error:
                warnings.append(f"{skill_file}: unable to read metadata: {error}")
                continue
            if metadata is None:
                warnings.append(f"{skill_file}: missing name or description in YAML frontmatter")
                continue

            name, description = metadata
            if name == SELF_NAME:
                continue

            real_path = str(candidate.resolve())
            if real_path in seen_real_paths:
                if real_path in skills_by_real_path:
                    skills_by_real_path[real_path]["installation_paths"].append(str(candidate.absolute()))
                continue
            seen_real_paths.add(real_path)

            if name in skills_by_name:
                skills_by_name[name]["shadowed_paths"].append(real_path)
                continue

            skill = {
                "name": name,
                "description": description,
                "path": str(candidate.absolute()),
                "real_path": real_path,
                "scope": root.scope,
                "source_root": str(root.path.absolute()),
                "installation_paths": [str(candidate.absolute())],
                "shadowed_paths": [],
            }
            skills_by_name[name] = skill
            skills_by_real_path[real_path] = skill

    return {
        "skills": sorted(skills_by_name.values(), key=lambda skill: skill["name"]),
        "warnings": warnings,
    }


def render_markdown(result: dict[str, list]) -> str:
    lines = ["| Skill | Scope | Description | Path |", "|---|---|---|---|"]
    for skill in result["skills"]:
        description = skill["description"].replace("|", "\\|").replace("\n", " ")
        lines.append(f"| `{skill['name']}` | `{skill['scope']}` | {description} | `{skill['path']}` |")
    if result["warnings"]:
        lines.extend(["", "Warnings:"])
        lines.extend(f"- {warning}" for warning in result["warnings"])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", action="append", default=[], metavar="[SCOPE=]PATH")
    parser.add_argument("--cwd", type=Path, default=Path.cwd())
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    args = parser.parse_args()

    roots = parse_root_specs(args.root) if args.root else default_roots(args.cwd)
    result = discover(roots)
    if args.format == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(render_markdown(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
