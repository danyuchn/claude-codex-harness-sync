#!/usr/bin/env python3
"""Inventory Claude and Codex harness files without modifying anything."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

HOME = Path.home()
EXCLUDED_DIRS = {
    ".git",
    ".bun",
    ".cache",
    ".codex",
    ".Codex",
    "node_modules",
    "Library",
    ".Trash",
    "dist",
    "build",
    "vendor",
    "__pycache__",
    "Caches",
}


def exists(path: Path) -> str | None:
    return str(path) if path.exists() else None


def list_paths(root: Path, patterns: list[str], max_items: int = 500) -> list[str]:
    if not root.exists():
        return []
    found: list[str] = []
    for pattern in patterns:
        for path in root.glob(pattern):
            if path.exists():
                found.append(str(path))
                if len(found) >= max_items:
                    return sorted(set(found))
    return sorted(set(found))


def find_project_claude_dirs(search_roots: list[Path], max_projects: int = 200) -> list[str]:
    found: list[str] = []
    seen: set[Path] = set()
    for root in search_roots:
        if not root.exists() or not root.is_dir():
            continue
        for current, dirs, _files in os.walk(root):
            current_path = Path(current)
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS and not d.endswith(".app")]
            if current_path.name == ".claude":
                if current_path == HOME / ".claude":
                    dirs[:] = []
                    continue
                if any(part in EXCLUDED_DIRS for part in current_path.parts):
                    dirs[:] = []
                    continue
                if current_path not in seen:
                    seen.add(current_path)
                    found.append(str(current_path))
                dirs[:] = []
                if len(found) >= max_projects:
                    return sorted(found)
    return sorted(found)


def inspect_claude_project(claude_dir: Path) -> dict:
    project = claude_dir.parent
    return {
        "project_root": str(project),
        "claude_dir": str(claude_dir),
        "claude_md": exists(project / "CLAUDE.md"),
        "claude_local_md": exists(project / "CLAUDE.local.md"),
        "claude_dir_claude_md": exists(claude_dir / "CLAUDE.md"),
        "agents_md": exists(project / "AGENTS.md"),
        "agents_override_md": exists(project / "AGENTS.override.md"),
        "mcp_json": exists(project / ".mcp.json"),
        "claude_settings": list_paths(claude_dir, ["settings*.json"]),
        "rules": list_paths(claude_dir / "rules", ["**/*.md"]),
        "skills": list_paths(claude_dir / "skills", ["*/SKILL.md"]),
        "codex_agents_skills": list_paths(project / ".agents" / "skills", ["*/SKILL.md"]),
        "codex_project_config": exists(project / ".codex" / "config.toml"),
        "codex_project_hooks_json": exists(project / ".codex" / "hooks.json"),
        "hooks": list_paths(claude_dir / "hooks", ["*"]),
    }


def inventory(search_home: bool) -> dict:
    claude_home = HOME / ".claude"
    codex_candidates = [HOME / ".codex", HOME / ".Codex"]
    codex_homes = [p for p in codex_candidates if p.exists()]

    search_roots = [HOME]
    if not search_home:
        search_roots = [Path.cwd()]

    project_dirs = [Path(p) for p in find_project_claude_dirs(search_roots)]
    official_codex_skill_roots = [HOME / ".agents" / "skills", Path("/etc/codex/skills")]

    return {
        "claude_global": {
            "home": str(claude_home),
            "claude_md": exists(claude_home / "CLAUDE.md"),
            "claude_local_md": exists(claude_home / "CLAUDE.local.md"),
            "agents_md": exists(claude_home / "AGENTS.md"),
            "settings_json": exists(claude_home / "settings.json"),
            "mcp_json": exists(claude_home / ".mcp.json"),
            "hooks": list_paths(claude_home / "hooks", ["*"]),
            "rules": list_paths(claude_home / "rules", ["**/*.md"]),
            "skills": list_paths(claude_home / "skills", ["*/SKILL.md"]),
            "memory_dirs": list_paths(claude_home / "projects", ["*/memory", "*/memory/*"]),
        },
        "codex_global": [
            {
                "home": str(home),
                "agents_md": exists(home / "AGENTS.md"),
                "config_toml": exists(home / "config.toml"),
                "hooks_json": exists(home / "hooks.json"),
                "hooks": list_paths(home / "hooks", ["*"]),
                "rules": list_paths(home / "rules", ["**/*"]),
                "skills": list_paths(home / "skills", ["*/SKILL.md"]),
                "memories": list_paths(home / "memories", ["**/*"]),
            }
            for home in codex_homes
        ],
        "codex_official_skill_roots": [
            {"root": str(root), "skills": list_paths(root, ["*/SKILL.md"])}
            for root in official_codex_skill_roots
            if root.exists()
        ],
        "claude_projects": [inspect_claude_project(path) for path in project_dirs],
    }


def markdown_report(data: dict) -> str:
    projects = data["claude_projects"]
    lines = [
        "## Harness Inventory",
        "",
        "### Claude Global",
        f"- Home: `{data['claude_global']['home']}`",
        f"- Hooks: {len(data['claude_global']['hooks'])}",
        f"- Rules: {len(data['claude_global']['rules'])}",
        f"- Skills: {len(data['claude_global']['skills'])}",
        f"- Memory paths: {len(data['claude_global']['memory_dirs'])}",
        "",
        "### Codex Global",
    ]
    for codex in data["codex_global"]:
        lines.extend(
            [
                f"- Home: `{codex['home']}`",
                f"  - Hooks: {len(codex['hooks'])}",
                f"  - Rules: {len(codex['rules'])}",
                f"  - Local Codex skills: {len(codex['skills'])}",
                f"  - Memories: {len(codex['memories'])}",
            ]
        )
    official_roots = data.get("codex_official_skill_roots", [])
    lines.extend(["", "### Codex Official Skill Roots"])
    if not official_roots:
        lines.append("- None found")
    for root in official_roots:
        lines.append(f"- `{root['root']}`: {len(root['skills'])} skills")
    lines.extend(["", "### Claude Projects Found", f"- Count: {len(projects)}"])
    for project in projects[:80]:
        lines.append(f"- `{project['project_root']}`")
    if len(projects) > 80:
        lines.append(f"- ... {len(projects) - 80} more omitted")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["setup", "maintain"], default="setup")
    parser.add_argument("--format", choices=["json", "markdown"], default="markdown")
    parser.add_argument("--cwd-only", action="store_true")
    args = parser.parse_args()

    data = inventory(search_home=not args.cwd_only)
    data["mode"] = args.mode
    if args.format == "json":
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(markdown_report(data))


if __name__ == "__main__":
    main()
