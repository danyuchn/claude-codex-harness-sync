#!/usr/bin/env python3
"""Classify high-level Claude/Codex harness drift from inventory JSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def skill_names(paths: list[str]) -> set[str]:
    names: set[str] = set()
    for raw in paths:
        path = Path(raw)
        if path.name == "SKILL.md":
            names.add(path.parent.name)
    return names


def classify(data: dict) -> dict:
    claude = data["claude_global"]
    codex = data["codex_global"][0] if data["codex_global"] else {}

    claude_skills = skill_names(claude.get("skills", []))
    codex_skills = skill_names(codex.get("skills", []))
    for root in data.get("codex_official_skill_roots", []):
        codex_skills.update(skill_names(root.get("skills", [])))

    projects_with_imports = []
    for project in data.get("claude_projects", []):
        if project.get("claude_md"):
            try:
                text = Path(project["claude_md"]).read_text(errors="ignore")
                if "\n@" in text or text.lstrip().startswith("@"):
                    projects_with_imports.append(project["project_root"])
            except OSError:
                pass

    return {
        "missing_in_codex": {
            "global_agents_md": not bool(codex.get("agents_md")),
            "hooks_json": bool(claude.get("settings_json")) and not bool(codex.get("hooks_json")),
            "skills": sorted(claude_skills - codex_skills),
        },
        "manual_hook_translation": claude.get("hooks", []),
        "memory_migration_plan_needed": claude.get("memory_dirs", []),
        "claude_imports_need_flattening": projects_with_imports,
        "model_assisted_manual": [
            "Rewrite Claude hooks into Codex hooks after explaining target files and risks.",
            "Flatten or split Claude @ imports after showing the AGENTS.md impact.",
            "Draft MCP TOML with env placeholders only, then ask before writing.",
            "Classify Claude memory and ask before migrating selected items.",
            "Split oversized AGENTS.md into nested AGENTS.md, skills, or project docs after approval.",
        ],
        "user_owned_secret_steps": [
            "API key values",
            "OAuth tokens",
            "Cookies",
            "Private account authorizations",
        ],
        "codex_specific_preserve": codex.get("hooks", []),
        "project_candidates": data.get("claude_projects", []),
        "loss_report": [
            "Claude @ imports have no official Codex AGENTS.md import equivalent; flatten or use nested AGENTS.md.",
            "Claude hooks are schema-incompatible with Codex hooks; rewrite manually.",
            "Claude .claude/rules has no official Codex .codex/rules equivalent; map to AGENTS.md layering or user convention.",
            "MCP JSON/TOML auth and env semantics differ; migrate placeholders only.",
            "Memory is local generated state; classify before migrating.",
        ],
        "unsafe_to_copy": [
            "Claude settings hook blocks",
            "MCP inline environment values",
            "Secrets or token-like values",
            "Outgoing communication hooks",
            "Destructive command hooks",
        ],
    }


def markdown(result: dict) -> str:
    lines = [
        "## Harness Drift Classification",
        "",
        "### Missing In Codex",
    ]
    missing = result["missing_in_codex"]
    lines.append(f"- Global AGENTS.md missing: {missing['global_agents_md']}")
    lines.append(f"- hooks.json missing while Claude settings exist: {missing['hooks_json']}")
    lines.append(f"- Skills missing: {len(missing['skills'])}")
    for name in missing["skills"][:50]:
        lines.append(f"  - `{name}`")
    lines.extend(
        [
            "",
            "### Model-Assisted Hook Translation",
            f"- Claude hooks to review: {len(result['manual_hook_translation'])}",
            "",
            "### Memory",
            f"- Claude memory paths to classify: {len(result['memory_migration_plan_needed'])}",
            "",
            "### Model-Assisted Manual Work",
        ]
    )
    for item in result["model_assisted_manual"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "### User-Owned Secret Steps",
        ]
    )
    for item in result["user_owned_secret_steps"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "### Claude Imports Needing Flattening",
            f"- Projects: {len(result['claude_imports_need_flattening'])}",
            "",
            "### Preserve As Codex-Specific",
            f"- Existing Codex hooks: {len(result['codex_specific_preserve'])}",
            "",
            "### Loss Report",
        ]
    )
    for item in result["loss_report"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "### Unsafe To Copy",
        ]
    )
    for item in result["unsafe_to_copy"]:
        lines.append(f"- {item}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("inventory_json")
    parser.add_argument("--format", choices=["json", "markdown"], default="markdown")
    args = parser.parse_args()

    data = json.loads(Path(args.inventory_json).read_text())
    result = classify(data)
    if args.format == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(markdown(result))


if __name__ == "__main__":
    main()
