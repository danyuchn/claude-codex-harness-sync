---
name: claude-codex-harness-sync
description: "Audit, initialize, and maintain migration from a Claude Code harness to a Codex harness. Use for /claude-codex-harness-sync setup to inventory Claude global/project harnesses and produce a Codex migration plan, or /claude-codex-harness-sync maintain to compare existing Claude/Codex harness drift and apply only confirmed safe syncs. Never modifies .claude."
allowed-tools: Bash, Read, Edit, Write, Glob, Grep
---

# Claude to Codex Harness Sync

This skill has two modes:

- `setup`: first-time inventory and migration planning from Claude Code to Codex.
- `maintain`: ongoing drift audit and safe synchronization from Claude Code to Codex.

Default behavior is **dry-run audit**. Apply changes only when the user explicitly asks to apply safe changes after seeing the report.

This is a collaborative migration tool, not a passive checklist. Handle work in three tiers:

1. `auto-apply-after-confirmation`: low-risk Codex-side edits the model can apply once the user says to apply safe changes.
2. `model-assisted-manual`: risky or semantic changes the model should still handle, but only after explaining the exact files, intended edits, risks, backup/trial path, and validation plan, then receiving user approval.
3. `user-owned-secret-step`: secrets and account authorizations the model must not fill in; provide placeholders and clear instructions.

## Non-negotiable rules

- Treat Claude Code as the source to inspect, not a target to modify.
- Never edit, delete, move, or rewrite any file under `.claude` or `~/.claude`.
- Never copy secrets, tokens, inline env values, account credentials, or MCP keys into Codex.
- Do not blind-copy hooks. Claude hooks require model-assisted manual translation because event schemas and tool surfaces differ from Codex.
- Do not assume Claude `@` imports work in Codex. Official Codex AGENTS.md docs do not document inline `@` import expansion; flatten critical includes or use nested `AGENTS.md` / configured fallback filenames.
- In public/downloaded use, run setup and maintain in report-only mode first.

## Documentation freshness

At the start of setup or maintain, refresh official docs when internet access is available:

- Claude Code memory / CLAUDE.md / imports.
- Claude Code hooks.
- Claude Code skills.
- Claude Code MCP and settings.
- Codex AGENTS.md.
- Codex hooks.
- Codex skills.
- Codex config / MCP.

If live docs cannot be fetched, say so and continue using the skill's built-in rules plus the user's detected local structure. Do not silently pretend the docs are current.

## Official/current path assumptions

Use these paths unless the user's machine proves otherwise:

| Layer | Claude Code source | Codex target |
|---|---|---|
| Global instructions | `~/.claude/CLAUDE.md`, `~/.claude/AGENTS.md` if present | `~/.codex/AGENTS.md`, optional `AGENTS.override.md` |
| Project instructions | `<project>/CLAUDE.md`, `<project>/.claude/CLAUDE.md`, `CLAUDE.local.md` | `<project>/AGENTS.md`, nested `AGENTS.md`, optional fallback filenames |
| Hooks | `~/.claude/settings.json`, `.claude/settings*.json`, `~/.claude/hooks/` | `~/.codex/hooks.json`, `~/.codex/config.toml`, project `.codex/hooks.json` / `.codex/config.toml` |
| Rules | `~/.claude/rules/`, `<project>/.claude/rules/` | AGENTS.md layering, nested AGENTS.md, or user-specific Codex rules if already present |
| Skills | `~/.claude/skills/`, `<project>/.claude/skills/` | official Codex `.agents/skills/`, `$HOME/.agents/skills/`, or detected local Codex skill roots |
| Memory | `~/.claude/projects/*/memory/`, project docs | `~/.codex/memories/` if enabled, or project knowledge docs |
| MCP | Claude settings / `.mcp.json` | `~/.codex/config.toml` with `env_vars`, never inline secrets |

On macOS some installs expose both `~/.Codex` and `~/.codex`; inspect both, then use the one that actually exists and is active. If both resolve to the same files, report that once and avoid duplicate work.

## Mode selection

If the user does not specify a mode:

- Choose `setup` for phrases like "first time", "initial setup", "migrate to Codex", "initialize", "install Codex harness".
- Choose `maintain` for phrases like "sync", "update", "drift", "compare", "keep Codex aligned".
- If still ambiguous, ask one short question.

## Setup mode

Goal: discover the user's Claude Code harness and produce a migration plan for Codex.

1. Inventory global Claude and Codex harnesses:
   ```bash
   python3 scripts/inventory.py --mode setup --format markdown
   ```
2. Scan project-level Claude harnesses by finding `.claude` directories. Do not scan arbitrary directories as projects; a `.claude` folder is the project signal.
3. For each discovered project, inventory:
   - `CLAUDE.md`
   - `.claude/rules/`
   - `.claude/skills/*/SKILL.md`
   - `.claude/hooks/` if present
   - `.mcp.json` if present
4. Classify migration work:
   - `auto-apply-after-confirmation`: text/rules/skills with no secrets or side effects.
   - `model-assisted-manual`: CLAUDE.md imports, hooks, MCP drafts, AGENTS.md splitting, memory routing, path casing, Claude-only wording.
   - `user-owned-secret-step`: API keys, OAuth tokens, cookies, account credentials, and secret values.
   - `codex-specific`: already intentionally different in Codex.
   - `unsafe`: secrets, credentials, MCP inline env values, outgoing comms, destructive commands.
   - `needs-user-decision`: deletions, trusted project changes, MCP server definitions, plugin-managed files.
5. Produce a loss report for anything that cannot be mapped exactly, especially hooks, `@` imports, permissions, MCP auth, plugin namespaces, commands, agents/subagents, and memory.
6. If the user later asks to apply changes, prefer a trial Codex home first, such as `/tmp/claude-codex-harness-sync-trial/.codex`, then show the generated files before touching the real Codex home.
7. Output the setup report. Do not modify files unless the user explicitly says to apply safe changes.

## Maintain mode

Goal: compare existing Claude and Codex harnesses and sync confirmed safe drift.

1. Inventory both sides:
   ```bash
   python3 scripts/inventory.py --mode maintain --format json > /tmp/harness-inventory.json
   python3 scripts/classify_drift.py /tmp/harness-inventory.json --format markdown
   ```
2. Compare only known corresponding surfaces:
   - `CLAUDE.md` vs `AGENTS.md`
   - `.claude/rules/` vs AGENTS.md layering or detected Codex rules convention
   - `.claude/skills/` vs `.agents/skills/` and detected Codex skill roots
   - Claude hook inventory vs Codex hook inventory as a translation checklist, not a patch.
   - Claude memory inventory vs Codex memory/project-doc destination plan.
3. Apply low-risk changes after explicit user confirmation:
   - AGENTS.md wording/pointer updates.
   - Project instruction/rules text updates in the user's established Codex convention.
   - Skill body updates with no new network calls, no outgoing comms, and no destructive behavior.
   - Path/reference corrections from Claude-style names to Codex-style names.
   - MCP env var name placeholders only, never values.
4. For high-risk changes, use model-assisted manual flow:
   - Explain exactly what will be changed and why.
   - List exact target files.
   - Describe non-equivalent behavior and risks.
   - Create a backup or trial output when practical.
   - Ask for explicit approval.
   - Apply the Codex-side change after approval.
   - Validate immediately.
5. Use model-assisted manual flow for:
   - Hooks.
   - MCP server definitions and approval modes.
   - Trusted projects or approval policies.
   - AGENTS.md flattening/splitting when large or import-heavy.
   - Memory migration.
   - Deletions.
   - Plugin/runtime-managed skills.
6. Never fill in:
   - Credentials or env values.
   - OAuth tokens.
   - Cookies.
   - Private account authorization.

## Hooks workflow

Hooks are not skipped. They are rewritten by the model after approval.

For each hook candidate:

1. Identify the Claude source hook and the behavior it enforces.
2. Identify the closest Codex event and handler shape.
3. State what is not equivalent.
4. Propose a Codex hook file and hooks.json/config change.
5. Ask for user approval.
6. Write only Codex-side files after approval.
7. Run automated tests when possible:
   - JSON/TOML parse checks.
   - `bash -n`.
   - Synthetic tool payload tests when the hook can be invoked safely.
8. If a behavior cannot be automatically tested, output a manual test checklist for the user.

## Memory migration

Memory is not copied blindly. Classify each memory item:

- `user-preference`: migrate only if it is durable, non-private, and useful to Codex.
- `project-fact`: prefer project docs or AGENTS.md if it belongs to a repo.
- `workflow-lesson`: prefer a skill, rule, or memory summary depending on trigger frequency.
- `private-sensitive`: keep out of Codex memory unless the user explicitly chooses otherwise.
- `stale-or-conflicting`: report only.

Codex memory output should be a plan first. After user confirmation, migrate only selected items to the right destination and validate for duplicates or conflicts.

## AGENTS.md size management

If migrated guidance would make AGENTS.md large or noisy:

- Keep only core always-needed rules in AGENTS.md.
- Move directory-specific guidance to nested AGENTS.md files.
- Move repeatable workflows into skills.
- Move long background material into project docs.
- If using fallback filenames or custom config, document it clearly.

Ask before splitting files, then perform the split after approval.

## MCP workflow

MCP migration is model-assisted manual work:

1. Read Claude MCP shape.
2. Draft Codex TOML using env var names or placeholders only.
3. Explain server name, command/URL, transport, env placeholders, approval mode, and risk.
4. Ask for user approval.
5. Update only the relevant MCP section after approval, preserving unrelated Codex config.
6. Validate TOML.
7. Test server listing/startup if available; otherwise provide manual test steps.

## Unknown environments

If expected paths or commands are missing:

- Report the exact missing path or command.
- Show what was detected instead.
- Infer likely cause when possible.
- Ask one concise question only if discovery cannot continue safely.
- Prefer detected local reality over defaults.
- Continue with a reduced dry-run report rather than failing silently.

## Validation

After any Codex-side change, run:

```bash
python3 scripts/validate_codex.py
```

Minimum checks:

- Parse `~/.codex/config.toml` or `~/.Codex/config.toml` with `tomllib`.
- Parse `~/.codex/hooks.json` or `~/.Codex/hooks.json` as JSON.
- Run `bash -n` on Codex hook scripts.
- Scan loaded skill names for duplicates.
- Scan candidate Codex files for secret-like strings without printing secret values.
- Confirm hooks are enabled only if the active Codex config supports and enables them; otherwise report hook files as inert.

## Report format

Use `references/output-formats.md`.

Keep reports concise, but always include:

- Mode used.
- Paths inspected.
- What is safe to apply.
- What needs translation.
- What must never be auto-applied.
- Validation results.
- Next command the user can run.
