# Harness Layer Map

Use this map when translating Claude Code harness behavior to Codex.

## Layers

1. Hooks
   - Claude: `~/.claude/settings.json`, `~/.claude/hooks/`, project `.claude/hooks/`.
   - Codex: `~/.codex/hooks.json`, `~/.codex/config.toml`, project `.codex/hooks.json` / `.codex/config.toml`, `~/.codex/hooks/`.
   - Policy: never auto-convert. Produce a translation plan.

2. Rules
   - Claude: `~/.claude/rules/`, project `.claude/rules/`, sometimes `@` imported by `CLAUDE.md`.
   - Codex: AGENTS.md layering, nested AGENTS.md, configured fallback filenames, or a user's existing Codex-specific rules convention.
   - Policy: convert `@` imports into flattened critical text, nested AGENTS.md, or explicit guidance. Do not assume Codex supports Claude-style inline `@` import expansion.

3. Memory
   - Claude: `~/.claude/projects/*/memory/`, project docs, prior session summaries.
   - Codex: `~/.codex/memories/` or project docs.
   - Policy: plan first. Do not blindly copy private or stale memory.

4. Skills
   - Claude: `~/.claude/skills/`, project `.claude/skills/`.
   - Codex official/project: `.agents/skills/` in the project or ancestors, `$HOME/.agents/skills`, `/etc/codex/skills`, plus any detected local/plugin skill roots.
   - Policy: safe to copy only when no side effects, no runtime-specific references, and no secrets.

5. Instructions
   - Claude: `CLAUDE.md`, `.claude/CLAUDE.md`, `CLAUDE.local.md`, `~/.claude/CLAUDE.md`.
   - Codex: `AGENTS.md`, `AGENTS.override.md`, and optional configured fallback filenames.
   - Policy: translate names, paths, import semantics, byte limits, and precedence.

## Project discovery

For project-level migration, treat a `.claude` directory as the strongest signal that Claude Code has touched or configured that project.

Scan for `.claude` directories while excluding common heavy directories:

- `.git`
- `node_modules`
- `Library`
- `.Trash`
- `dist`
- `build`
- `vendor`
- cache directories

Then inspect only the project root around that `.claude` folder.
