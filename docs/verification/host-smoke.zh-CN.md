# AletheiaOS Host Smoke Checklist

本文档用于验证 AletheiaOS 在真实 Codex 与 Claude Code 宿主中的加载路径。自动化测试已经覆盖 scaffold、runtime、checkpoint、model gate、overview、source inventory 和 Wiki handoff promotion；这里仅记录当前无法稳定非交互自动化的宿主验收。

## 前置条件

- 当前仓库位于 AletheiaOS checkout 根目录。
- 本机已安装 `python3`、`git`、`claude` 和 `codex`。
- 使用临时测试仓库，不要在含有未提交业务改动的项目中做 smoke。

## 版本记录

每次 smoke 先记录宿主和基础工具版本：

```bash
python3 --version
git --version
claude --version
codex --version
```

记录格式：

- Host:
- OS:
- Python:
- Git:
- Claude Code:
- Codex:
- AletheiaOS commit:

## 打包

```bash
python3 scripts/package_plugin.py --output /tmp/aletheia-os-dist
```

执行命令：见上方代码块。

期望结果：

验收：

- 输出目录存在：`/tmp/aletheia-os-dist/aletheia-os/`。
- 目录内包含 `.claude-plugin/`、`.codex-plugin/`、`skills/`、`agents/`、`codex-agents/`、`assets/`、`scripts/`、`docs/` 和 `README.zh-CN.md`。

实际结果：

- PASS/FAIL:
- stdout/stderr:

## Claude Code

```bash
cd /tmp/aletheia-os-dist/aletheia-os
claude plugin validate .
```

执行命令：见上方代码块。

期望结果：

验收：

- validation 没有报告 manifest、skills 或 agents 路径错误。
- 如果命令在本机版本挂起，记录 Claude Code 版本、命令输出和中断方式；不要把挂起结果标记为通过。

实际结果：

- PASS/FAIL:
- stdout/stderr:

项目级安装 smoke：

```bash
mkdir -p /tmp/aios-host-smoke-claude
cd /tmp/aios-host-smoke-claude
git init
claude plugin marketplace add /tmp/aletheia-os-dist/aletheia-os --scope project
claude plugin install aletheia-os@aletheia-os --scope project
python3 /tmp/aletheia-os-dist/aletheia-os/scripts/init_aletheia.py .
```

执行命令：见上方代码块。

期望结果：

验收：

- `.aletheia/START_HERE.md` 存在。
- `.claude/settings.json` 包含 SessionStart、PreToolUse、PostToolUse 和 Stop hooks。
- Claude Code 中可以看到 AletheiaOS skills。
- `truth-auditor`、`evidence-curator`、`architecture-reviewer` 可作为只读 truth-layer review agents 使用。

实际结果：

- PASS/FAIL:
- stdout/stderr:

## Codex

```bash
codex plugin marketplace add /tmp/aletheia-os-dist/aletheia-os
```

然后在 Codex 中打开 `/plugins`，启用 `aletheia-os`。

执行命令：见上方代码块。

期望结果：

- Codex marketplace 接受本地 AletheiaOS plugin 路径。
- `/plugins` 可以启用 `aletheia-os`。

实际结果：

- PASS/FAIL:
- stdout/stderr:

项目级 Codex agents smoke：

```bash
mkdir -p /tmp/aios-host-smoke-codex/.codex/agents
cp /tmp/aletheia-os-dist/aletheia-os/codex-agents/*.toml /tmp/aios-host-smoke-codex/.codex/agents/
cd /tmp/aios-host-smoke-codex
git init
python3 /tmp/aletheia-os-dist/aletheia-os/scripts/init_aletheia.py .
```

执行命令：见上方代码块。

期望结果：

验收：

- Codex `/plugins` 中 AletheiaOS 已启用。
- AletheiaOS skills 可被调用。
- `.codex/agents/truth-auditor.toml`、`.codex/agents/evidence-curator.toml`、`.codex/agents/architecture-reviewer.toml` 存在。
- Codex 能执行 `python3 .aletheia/bin/orient.py`、`python3 .aletheia/bin/validate.py` 和 `python3 .aletheia/bin/checkpoint.py --dry-run --no-model-gate`。

实际结果：

- PASS/FAIL:
- stdout/stderr:

## 失败记录

每次 smoke 失败都记录：

- 宿主名称和版本；
- 执行命令；
- stdout/stderr；
- 是否可复现；
- 是否影响 core runtime，还是仅影响宿主插件加载。
