# Output Formats

## Setup report

```markdown
## Harness Setup Plan

### Inspected
- Claude global:
- Codex global:
- Claude projects found:

### Claude Harness Inventory
- Instructions:
- Hooks:
- Rules:
- Skills:
- Memory:
- MCP:

### Recommended Codex Migration
- Auto-apply after confirmation:
- Model-assisted manual work:
- User-owned secret steps:
- Hook translation plan:
- Memory migration plan:
- AGENTS.md size/splitting plan:
- MCP conversion plan:
- Loss report:
- Unsafe / do not migrate:
- Needs user decision:
- Trial Codex home:

### Proposed Codex Files
- `~/.codex/AGENTS.md`
- `~/.codex/hooks.json`
- `~/.codex/hooks/...`
- `~/.codex/skills/...`
- `<project>/AGENTS.md`
- `<project>/.codex/...`

### Next Step
Run: `/claude-codex-harness-sync apply safe changes`
```

## Maintain report

```markdown
## Harness Maintenance

### Drift Summary
- Missing in Codex:
- Stale in Codex:
- Codex-specific, preserve:
- Unsafe to copy:
- Needs user decision:

### Applied
- None, dry-run mode.

### Model-Assisted Manual Plan
- Proposed changes:
- Files to touch:
- Risks:
- Validation:
- Approval needed:

### Loss Report
- Hooks:
- Imports:
- MCP auth:
- Commands / subagents:
- Memory:

### Validation
- hooks.json:
- config.toml:
- hook shell syntax:
- duplicate skills:
- secret scan:

### Next Step
```

## Apply report

```markdown
## Harness Sync Applied

### Changed Files
- `file://...`

### Skipped
- ...

### Validation
- ...
```
