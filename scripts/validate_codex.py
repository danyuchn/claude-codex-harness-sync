#!/usr/bin/env python3
"""Validate Codex harness syntax and obvious hygiene issues."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tomllib
from collections import defaultdict
from pathlib import Path

HOME = Path.home()
SECRET_RE = re.compile(
    r"(sk-[A-Za-z0-9_-]{20,}|pro_[A-Za-z0-9_-]{20,}|api[_-]?key\s*=\s*['\"][^'\"]+['\"])",
    re.IGNORECASE,
)


def codex_homes() -> list[Path]:
    homes: list[Path] = []
    seen: set[Path] = set()
    for path in [HOME / ".codex", HOME / ".Codex"]:
        if not path.exists():
            continue
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        homes.append(path)
    return homes


def check_json(path: Path) -> tuple[bool, str]:
    if not path.exists():
        return True, "missing"
    try:
        json.loads(path.read_text())
        return True, "ok"
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def check_toml(path: Path) -> tuple[bool, str]:
    if not path.exists():
        return True, "missing"
    try:
        tomllib.loads(path.read_text())
        return True, "ok"
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def check_bash(path: Path) -> tuple[bool, str]:
    result = subprocess.run(["bash", "-n", str(path)], capture_output=True, text=True)
    if result.returncode == 0:
        return True, "ok"
    return False, result.stderr.strip()


def skill_name_duplicates(home: Path) -> dict[str, list[str]]:
    names: dict[str, list[str]] = defaultdict(list)
    roots = [home / "skills", HOME / ".agents" / "skills", Path("/etc/codex/skills")]
    seen_roots: set[Path] = set()
    for root in roots:
        if not root.exists():
            continue
        resolved = root.resolve()
        if resolved in seen_roots:
            continue
        seen_roots.add(resolved)
        for skill in root.glob("*/SKILL.md"):
            text = skill.read_text(errors="ignore")
            match = re.search(r"^name:\s*[\"']?([^\"'\n]+)", text, flags=re.MULTILINE)
            if match:
                names[match.group(1).strip()].append(str(skill))
    return {name: paths for name, paths in names.items() if len(paths) > 1}


def secret_hits(home: Path) -> list[str]:
    hits: list[str] = []
    for path in list((home / "hooks").glob("*")) + [home / "config.toml", home / "AGENTS.md"]:
        if not path.exists() or not path.is_file():
            continue
        text = path.read_text(errors="ignore")
        if SECRET_RE.search(text):
            hits.append(str(path))
    return hits


def main() -> None:
    failures = 0
    for home in codex_homes():
        print(f"## {home}")
        ok, msg = check_json(home / "hooks.json")
        print(f"- hooks.json: {msg}")
        failures += 0 if ok else 1

        ok, msg = check_toml(home / "config.toml")
        print(f"- config.toml: {msg}")
        failures += 0 if ok else 1

        hook_failures = []
        for hook in (home / "hooks").glob("*.sh"):
            ok, msg = check_bash(hook)
            if not ok:
                hook_failures.append(f"{hook}: {msg}")
        print(f"- hook shell syntax: {'ok' if not hook_failures else len(hook_failures)}")
        failures += len(hook_failures)

        duplicates = skill_name_duplicates(home)
        print(f"- duplicate skill names: {'none' if not duplicates else ', '.join(duplicates)}")
        failures += len(duplicates)

        secrets = secret_hits(home)
        print(f"- secret-like files: {'none' if not secrets else len(secrets)}")
        for path in secrets:
            print(f"  - {path}")
        failures += len(secrets)

    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
