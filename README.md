# Claude Codex Harness Sync

[繁體中文](#繁體中文) | [English](#english)

Public repository: https://github.com/danyuchn/claude-codex-harness-sync

## 繁體中文

這是一個 Codex skill，用來盤點、初始化、維護 Claude Code harness 到 Codex harness 的遷移。

它不是把 `.claude` 整包複製到 Codex，而是先做 audit，再把能安全同步的內容翻譯成 Codex 端可用的形式。高風險項目會由模型協助人工處理：先說明要改什麼、會碰哪些檔案、風險是什麼、怎麼驗證，再等使用者確認後才改 Codex 端檔案。

### 功能

- 盤點全域 Claude / Codex harness 檔案。
- 找出電腦上曾被 Claude Code 使用過的專案，也就是含 `.claude` 的資料夾。
- `setup` 模式：產生第一次遷移到 Codex 的盤點與計畫。
- `maintain` 模式：產生 Claude / Codex 之間的差異報告。
- 將 hooks、MCP、memory、imports、大型 instruction files 視為模型協助人工處理項目。
- 永遠不修改 `.claude` 或 `~/.claude`。
- 永遠不把 secret values 複製到 Codex。

### 安裝

Clone 或下載這個 repo，然後複製到 Codex skills 目錄：

```bash
git clone https://github.com/danyuchn/claude-codex-harness-sync.git
mkdir -p ~/.codex/skills
cp -R claude-codex-harness-sync ~/.codex/skills/
```

接著在 Codex 裡使用：

```text
/claude-codex-harness-sync setup
```

或：

```text
/claude-codex-harness-sync maintain
```

### 兩種模式

`setup` 用於第一次遷移規劃。它會掃描 `~/.claude`、`~/.codex`、`~/.Codex`，以及所有包含 `.claude` 的專案資料夾。

`maintain` 用於日常維護。它會比較 Claude 和 Codex 已知的 harness surfaces，並分類哪些可以安全套用、哪些需要模型協助翻譯、哪些必須由使用者自己處理。

### 安全模型

這個 skill 把工作分成三層：

- `auto-apply-after-confirmation`：低風險 Codex 端變更，使用者確認後可由模型套用。
- `model-assisted-manual`：高風險或語意轉換工作，由模型說明、請求確認、改 Codex 端檔案、立即驗證。
- `user-owned-secret-step`：API keys、OAuth tokens、cookies、帳號授權值由使用者自己處理；模型只寫 placeholder 或 env var 名稱。

### 本機指令

Dry-run inventory：

```bash
python3 scripts/inventory.py --mode setup --format markdown
```

Drift classification：

```bash
python3 scripts/inventory.py --mode maintain --format json > /tmp/harness-inventory.json
python3 scripts/classify_drift.py /tmp/harness-inventory.json --format markdown
```

Validate Codex harness syntax：

```bash
python3 scripts/validate_codex.py
```

### 授權

MIT

## English

Audit, initialize, and maintain migration from a Claude Code harness to a Codex harness.

This repository is packaged as a Codex skill. It helps users inspect their Claude Code setup, map it to Codex surfaces, and apply only confirmed Codex-side changes.

It does not copy `.claude` wholesale into Codex. It audits first, then translates safe items into Codex-compatible surfaces. Risky items are handled as model-assisted manual work: the model explains the target files, risks, backup or trial path, and validation plan, then waits for user approval before editing Codex-side files.

### What It Does

- Inventories global Claude and Codex harness files.
- Finds project-level `.claude` folders as Claude-used project signals.
- Produces a setup migration plan for first-time Codex harness creation.
- Produces a maintain drift report for ongoing Claude/Codex alignment.
- Treats hooks, MCP, memory, imports, and large instruction files as model-assisted manual work.
- Never edits `.claude` or `~/.claude`.
- Never copies secret values into Codex.

### Install

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

### Modes

`setup` is for first-time migration planning. It scans `~/.claude`, `~/.codex`, `~/.Codex`, and project folders that contain `.claude`.

`maintain` is for ongoing drift checks. It compares known Claude and Codex harness surfaces and classifies what can be applied safely, what needs model-assisted translation, and what must remain user-owned.

### Safety Model

The skill uses three tiers:

- `auto-apply-after-confirmation`: low-risk Codex-side edits after user confirmation.
- `model-assisted-manual`: risky or semantic changes handled by the model after it explains the target files, risks, backup/trial path, and validation plan.
- `user-owned-secret-step`: API keys, OAuth tokens, cookies, and account authorization values are handled by the user.

### Local Commands

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

### License

MIT
