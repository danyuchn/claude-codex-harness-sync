# Risk Policy

## Auto-apply after user asks to apply safe changes

- Add or update Codex AGENTS.md prose.
- Add or update the user's established Codex rules/instruction convention.
- Add or update Codex skills that are pure instructions.
- Fix path names from Claude-specific paths to Codex-specific paths.
- Add documentation notes that explain a skipped manual migration.

## Model-assisted manual work

- Hooks: rewrite by model, never copy directly.
- Claude `settings.json` hook matchers.
- Claude `@` import patterns.
- MCP server definitions and approval modes.
- Commands that depend on Claude-only tools.
- Memory with unclear privacy or freshness.
- AGENTS.md splitting when content would become too large.
- Plugin/runtime-managed files.

For every model-assisted manual item, the model must say what it will change, why, which files will be touched, what could go wrong, and how it will validate. Then ask for approval before editing.

## Never auto-apply

- Writes under `.claude` or `~/.claude`.
- Deletions.
- Trusted project or approval-policy changes without explicit approval.
- Credential, token, API key, cookie, or account secret values.
- Gmail, Slack, LINE, or other outgoing communication behavior.
- Destructive command behavior.
- Blind overwrite of plugin/runtime-managed files.

## Secret handling

When scanning for secrets:

- Report file path and category only.
- Do not print the secret value.
- Prefer env var references such as `env_vars = ["NAME"]`.
- The user owns the real secret value; the model only writes placeholders or env var names.
- If a real secret appears in a committed file, tell the user rotation may be needed.
