# Claude Codex Harness Sync

Audit, initialize, and maintain migration from a Claude Code harness to a Codex harness.

This repository is packaged as a Codex skill. It helps users inspect their Claude Code setup, map it to Codex surfaces, and apply only confirmed Codex-side changes.

Public repository: https://github.com/danyuchn/claude-codex-harness-sync

## What It Does

- Inventories global Claude and Codex harness files.
- Finds project-level `.claude` folders as Claude-used project signals.
- Produces a setup migration plan for first-time Codex harness creation.
- Produces a maintain drift report for ongoing Claude/Codex alignment.
- Treats hooks, MCP, memory, imports, and large instruction files as model-assisted manual work.
- Never edits `.claude` or `~/.claude`.
- Never copies secret values into Codex.

## Install

Clone or download this repository, then copy the folder into your Codex skills directory:

```bash
git clone https://github.com/danyuchn/claude-codex-harness-sync.git
mkdir -p ~/.codex/skills
cp -R claude-codex-harness-sync ~/.codex/skills/
```

Then ask Codex:

```text
/claude-codex-harness-sync setup
```

or:

```text
/claude-codex-harness-sync maintain
```

## Modes

`setup` is for first-time migration planning. It scans `~/.claude`, `~/.codex`, `~/.Codex`, and project folders that contain `.claude`.

`maintain` is for ongoing drift checks. It compares known Claude and Codex harness surfaces and classifies what can be applied safely, what needs model-assisted translation, and what must remain user-owned.

## Safety Model

The skill uses three tiers:

- `auto-apply-after-confirmation`: low-risk Codex-side edits after user confirmation.
- `model-assisted-manual`: risky or semantic changes handled by the model after it explains the target files, risks, backup/trial path, and validation plan.
- `user-owned-secret-step`: API keys, OAuth tokens, cookies, and account authorization values are handled by the user.

## Local Commands

Dry-run inventory:

```bash
python3 scripts/inventory.py --mode setup --format markdown
```

Drift classification:

```bash
python3 scripts/inventory.py --mode maintain --format json > /tmp/harness-inventory.json
python3 scripts/classify_drift.py /tmp/harness-inventory.json --format markdown
```

Validate Codex harness syntax:

```bash
python3 scripts/validate_codex.py
```

## License

MIT
